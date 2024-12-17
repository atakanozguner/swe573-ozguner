from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils import get_current_user
from app.schemas import PostCreate, Post
from app.models import Post as PostModel, User
from typing import List

router = APIRouter()


@router.post("/posts", response_model=Post)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = PostModel(**post.dict(), owner_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/posts", response_model=List[Post])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).all()
