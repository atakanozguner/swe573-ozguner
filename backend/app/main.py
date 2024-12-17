from fastapi import FastAPI, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from .routers import post
from .database import engine, Base, get_db  # Import get_db here
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, utils
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import requests

logging.basicConfig(level=logging.INFO)

load_dotenv()

Base.metadata.create_all(bind=engine)
# Load environment variables

# Environment variable loading with defaults and validation
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

logging.info(f"DEBUG: SECRET_KEY is: {SECRET_KEY}")

# Initialize database tables

app = FastAPI()

os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl})
        super().__init__(flows=flows)


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="login")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for modular endpoints
app.include_router(
    post.router,
    prefix="",
    tags=["posts"],
    dependencies=[Depends(utils.get_current_user)],
)
app.state.SECRET_KEY = SECRET_KEY
app.state.ALGORITHM = ALGORITHM


@app.get("/")
def read_root():
    return {"message": "Welcome to the SWE573 - root endpoint"}


@app.get("/tags/search", response_model=list[dict])
def search_tags(query: str):
    response = requests.get(
        "https://www.wikidata.org/w/api.php",
        params={
            "action": "wbsearchentities",
            "language": "en",
            "format": "json",
            "search": query,
        },
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error fetching tags from Wikidata")

    data = response.json()
    return [
        {"label": item["label"], "description": item.get("description", "")}
        for item in data.get("search", [])
    ]


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
    if not db_user or not utils.verify_password(
        form_data.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Create the access token
    access_token = utils.create_access_token(
        data={"sub": db_user.username},
        secret_key=app.state.SECRET_KEY,
        algorithm=app.state.ALGORITHM,
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    # Return the token in an HTTP-only cookie
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # Set to True in production with HTTPS
    )
    return response


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@app.get("/users/me")
def get_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(utils.get_current_user),
):
    return {"username": current_user.username}


@app.get("/health/db")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        # Use text() to execute a raw SQL query
        result = db.execute(text("SELECT 1"))
        if result:
            return {"status": "Database is connected!"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection failed")
