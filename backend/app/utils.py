import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.security import OAuth2PasswordBearer, OAuth2
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

import os
import logging

logging.basicConfig(level=logging.INFO)


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str):
        self.tokenUrl = tokenUrl
        super().__init__(flows={"password": {"tokenUrl": tokenUrl}})

    async def __call__(self, request: Request) -> Optional[str]:
        # Check for Authorization header
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() == "bearer":
            return param

        # Fallback: Check for token in cookies
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return token


# Setup bcrypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme to extract the token
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="login")

# Environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Function to verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict, secret_key: str, algorithm: str, expires_delta: int
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    logging.info(f"DEBUG: Payload for token creation: {to_encode}")
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    logging.info(f"DEBUG: Token created: {token}")
    return token


def verify_token(token: str):
    try:
        logging.info(f"DEBUG: Verifying token: {token}")
        logging.info(
            f"DEBUG: Using SECRET_KEY: {SECRET_KEY} and ALGORITHM: {ALGORITHM}"
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logging.info(f"DEBUG: Decoded payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logging.error("DEBUG: Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logging.error(f"DEBUG: Invalid token - {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    logging.info(f"DEBUG: Received token in Authorization header: {token}")
    payload = verify_token(token)  # No need to pass SECRET_KEY or ALGORITHM
    username: str = payload.get("sub")
    if not username:
        logging.error("DEBUG: Invalid token payload - 'sub' claim missing")
        raise HTTPException(status_code=401, detail="Invalid token payload")
    logging.info(f"DEBUG: Token belongs to user: {username}")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logging.error("DEBUG: User not found in database")
        raise HTTPException(status_code=404, detail="User not found")
    return user
