from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils import get_current_user
from app.schemas import (
    PostCreate,
    Post,
    PostWithComments,
    Comment,
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

router = APIRouter()


@router.post("/posts", response_model=Post)
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    material: Optional[str] = Form(None),
    size: Optional[str] = Form(None),
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
        # Create a directory if it doesn't exist
        os.makedirs("static/images", exist_ok=True)

        # Generate a unique filename
        unique_name = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join("static", "images", unique_name)

        # Save the image to disk
        contents = await image.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Store a path or URL in the database
        # Assuming you serve static files from /static/ route
        image_url = f"/static/images/{unique_name}"

    # Create the post object using models.Post
    db_post = PostModel(
        title=title,
        description=description,
        material=material,
        size=size,
        color=color,
        shape=shape,
        weight=weight,
        location=location,
        smell=smell,
        taste=taste,
        origin=origin,
        image_url=image_url,
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
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts/{post_id}/comments", response_model=Comment)
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
    return db_comment


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

    existing_vote = (
        db.query(CommentVote)
        .filter(
            CommentVote.comment_id == comment_id, CommentVote.user_id == current_user.id
        )
        .first()
    )

    if existing_vote:
        # Update existing vote
        existing_vote.is_upvote = vote.is_upvote
    else:
        # Create new vote
        new_vote = CommentVote(
            comment_id=comment_id, user_id=current_user.id, is_upvote=vote.is_upvote
        )
        db.add(new_vote)

    db.commit()
    db.refresh(db_comment)

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

    # Return updated comment data with score
    return CommentWithScore(
        id=db_comment.id,
        post_id=db_comment.post_id,
        user_id=db_comment.user_id,
        content=db_comment.content,
        score=score,
    )
