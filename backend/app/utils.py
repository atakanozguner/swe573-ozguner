import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Setup bcrypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Function to create a JWT access token
def create_access_token(
    data: dict, secret_key: str, algorithm: str, expires_delta: int
) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


# Function to verify a JWT token
def verify_token(token: str, secret_key: str, algorithm: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
