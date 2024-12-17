from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.utils import get_current_user
from app.schemas import (
    PostCreate,
    Post,
    PostWithComments,
    CommentCreate,
    CommentVoteCreate,
    CommentWithScore,
)
from app.models import Post as PostModel
from app.models import Comment as CommentModel
from app.models import User, CommentVote
from typing import List, Optional
import uuid
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()


# @router.get("/tags/search", response_model=List[dict])
# def search_tags(query: str, db: Session = Depends(get_db)):
#     # Fetch results from Wikidata
#     response = requests.get(
#         "https://www.wikidata.org/w/api.php",
#         params={
#             "action": "wbsearchentities",
#             "language": "en",
#             "format": "json",
#             "search": query,
#         },
#     )
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Error fetching tags from Wikidata")

#     data = response.json()
#     return [
#         {"label": item["label"], "description": item.get("description", "")}
#         for item in data.get("search", [])
#     ]


@router.post("/posts", response_model=Post)
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),  # Accept tags as a list
    material: Optional[str] = Form(None),
    length: Optional[str] = Form(None),
    width: Optional[str] = Form(None),
    height: Optional[str] = Form(None),
    color: Optional[str] = Form(None),
    shape: Optional[str] = Form(None),
    weight: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    smell: Optional[str] = Form(None),
    taste: Optional[str] = Form(None),
    origin: Optional[str] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url = None
    if image:
        os.makedirs("static/images", exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join("static", "images", unique_name)

        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        image_url = f"/static/images/{unique_name}"

    db_post = PostModel(
        title=title,
        description=description,
        material=material,
        length=length,
        width=width,
        height=height,
        color=color,
        shape=shape,
        weight=weight,
        location=location,
        smell=smell,
        taste=taste,
        origin=origin,
        image_url=image_url,
        tags=tags,
        owner_id=current_user.id,
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/posts", response_model=List[Post])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).all()


@router.get("/posts/{post_id}", response_model=PostWithComments)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(PostModel)
        .options(selectinload(PostModel.comments).selectinload(CommentModel.user))
        .filter(PostModel.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Calculate score for each comment
    for c in post.comments:
        upvotes = (
            db.query(CommentVote)
            .filter(CommentVote.comment_id == c.id, CommentVote.is_upvote == True)
            .count()
        )
        downvotes = (
            db.query(CommentVote)
            .filter(CommentVote.comment_id == c.id, CommentVote.is_upvote == False)
            .count()
        )
        c.score = upvotes - downvotes

    return post


@router.post("/posts/{post_id}/comments", response_model=CommentWithScore)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = CommentModel(
        post_id=post.id, user_id=current_user.id, content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    return CommentWithScore(
        id=db_comment.id,
        post_id=db_comment.post_id,
        user_id=db_comment.user_id,
        content=db_comment.content,
        score=0,
        user={
            "id": db_comment.user.id,
            "username": db_comment.user.username,
        },  # Include user info
    )


@router.post("/comments/{comment_id}/vote", response_model=CommentWithScore)
def vote_on_comment(
    comment_id: int,
    vote: CommentVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_comment = db.query(CommentModel).filter(CommentModel.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check existing votes
    existing_vote = (
        db.query(CommentVote)
        .filter(
            CommentVote.comment_id == comment_id, CommentVote.user_id == current_user.id
        )
        .first()
    )

    if existing_vote:
        existing_vote.is_upvote = vote.is_upvote
    else:
        new_vote = CommentVote(
            comment_id=comment_id, user_id=current_user.id, is_upvote=vote.is_upvote
        )
        db.add(new_vote)

    db.commit()

    # Calculate score
    upvotes = (
        db.query(CommentVote)
        .filter(CommentVote.comment_id == comment_id, CommentVote.is_upvote == True)
        .count()
    )
    downvotes = (
        db.query(CommentVote)
        .filter(CommentVote.comment_id == comment_id, CommentVote.is_upvote == False)
        .count()
    )
    score = upvotes - downvotes

    # Refresh to include user relationship
    db.refresh(db_comment)

    return CommentWithScore(
        id=db_comment.id,
        post_id=db_comment.post_id,
        user_id=db_comment.user_id,
        content=db_comment.content,
        score=score,
        user={
            "id": db_comment.user.id,
            "username": db_comment.user.username,
        },  # Include user info
    )
