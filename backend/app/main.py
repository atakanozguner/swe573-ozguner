from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .routers import post
from .database import engine, Base, SessionLocal
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import models, schemas, utils
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

# Environment variable loading with defaults and validation
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # You can restrict this to ["http://localhost:5000"] for more security
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Include routers for modular endpoints
app.include_router(post.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the SWE573 - root endpoint"}


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(models.User).filter(models.User.username == user.username).first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = utils.hash_password(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    db_user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    # print(db_user)
    # print(form_data.username)
    # print(form_data.password)
    if not db_user or not utils.verify_password(
        form_data.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = utils.create_access_token(
        data={"sub": db_user.username},
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


# Health check endpoint for verifying DB connection
@app.get("/health/db")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        # Use text() to execute a raw SQL query
        result = db.execute(text("SELECT 1"))
        if result:
            return {"status": "Database is connected!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection failed")
