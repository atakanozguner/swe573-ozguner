from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import desc, func, or_
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
    PostWithTags,
    PostWithDetails,
)
from app.models import Post as PostModel
from app.models import Comment as CommentModel
from app.models import User, CommentVote, Tag, PostInterest
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


@router.post("/posts", response_model=PostWithTags)
async def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    material: Optional[str] = Form(None),
    length: Optional[float] = Form(None),
    width: Optional[float] = Form(None),
    height: Optional[float] = Form(None),
    color: Optional[str] = Form(None),
    shape: Optional[str] = Form(None),
    weight: Optional[float] = Form(None),
    location: Optional[str] = Form(None),
    smell: Optional[str] = Form(None),
    taste: Optional[str] = Form(None),
    origin: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),  # Accept tags as a list of JSON strings
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Handle image upload
    image_url = None
    if image:
        os.makedirs("static/images", exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join("static", "images", unique_name)

        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/static/images/{unique_name}"

    # Create post
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
        owner_id=current_user.id,
    )

    # Handle tags
    if tags:
        for tag_info in tags:  # Expecting tags as list of strings or objects
            # Check if tag_info is a dictionary or string
            if isinstance(tag_info, dict):
                label = tag_info.get("label")
                wikidata_url = tag_info.get("wikidata_url")
                description = tag_info.get("description")
            else:  # If it's a string, default other fields to placeholders
                label = tag_info
                wikidata_url = "https://www.wikidata.org"  # Default base URL
                description = "No description available"

            # Check if the tag already exists
            existing_tag = db.query(Tag).filter(Tag.label == label).first()

            if not existing_tag:
                # Create a new tag with default or provided values
                new_tag = Tag(
                    label=label, wikidata_url=wikidata_url, description=description
                )
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                tag_object = new_tag
            else:
                tag_object = existing_tag

            # Associate the tag with the post
            db_post.tags.append(tag_object)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.get("/posts", response_model=List[Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).all()

    # Convert tags to serialized format for each post
    serialized_posts = []
    for post in posts:
        serialized_post = post.__dict__.copy()
        serialized_post["tags"] = (
            [
                {
                    "label": tag.label,
                    "wikidata_url": tag.wikidata_url,
                    "description": tag.description,
                }
                for tag in post.tags
            ]
            if post.tags
            else []
        )
        serialized_posts.append(serialized_post)
    return serialized_posts


@router.get("/posts/hot", response_model=List[PostWithTags])
def get_hot_posts(db: Session = Depends(get_db)):
    """
    Fetch posts ordered by interest count in descending order.
    """
    posts = (
        db.query(PostModel)
        .outerjoin(
            PostInterest, PostModel.id == PostInterest.post_id
        )  # Join post_interests
        .group_by(PostModel.id)  # Group by post to allow counting interests
        .order_by(desc(func.count(PostInterest.id)))  # Count interest records
        .all()
    )
    return posts


@router.get("/posts/search", response_model=List[PostWithTags])
def search_posts(query: str, db: Session = Depends(get_db)):
    """
    Search posts based on query string. Matches title and description.
    """
    if not query:
        return []

    posts = (
        db.query(PostModel)
        .filter(
            or_(
                PostModel.title.ilike(f"%{query}%"),
                PostModel.description.ilike(f"%{query}%"),
            )
        )
        .all()
    )
    return posts


@router.get("/posts/{post_id}", response_model=PostWithDetails)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(PostModel)
        .options(
            selectinload(PostModel.comments).selectinload(
                CommentModel.user
            ),  # Load comments with users
            selectinload(PostModel.tags),  # Load tags
        )
        .filter(PostModel.id == post_id)
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Calculate scores for comments
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


@router.post("/posts/{post_id}/interested")
def toggle_interest(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if user has already shown interest
    existing_interest = (
        db.query(PostInterest)
        .filter_by(post_id=post_id, user_id=current_user.id)
        .first()
    )

    if existing_interest:
        db.delete(existing_interest)  # Remove interest if already present
    else:
        new_interest = PostInterest(post_id=post_id, user_id=current_user.id)
        db.add(new_interest)

    db.commit()

    # Return updated interest count
    interest_count = db.query(PostInterest).filter_by(post_id=post_id).count()
    return {"interest_count": interest_count}
