from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .routers import post
from .database import engine, Base, SessionLocal

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Include routers
app.include_router(post.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the SWE573 - root endpoint"}


# Health check endpoint to verify DB connection
@app.get("/health/db")
def check_db_connection(
    db: Session = Depends(get_db),
):  # Use get_db with Depends    try:
    try:
        # Use text() to execute raw SQL query
        result = db.execute(text("SELECT 1"))
        if result:
            return {"status": "Database is connected!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")
