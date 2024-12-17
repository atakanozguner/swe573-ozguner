from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, selectinload, joinedload
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
    tags: Optional[List[str]] = Form(None),  # Accept tags as a list of strings or JSON
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint to create a post with all fields, including tags and image upload.
    """
    # Handle image upload
    image_url = None
    if image:
        os.makedirs("static/images", exist_ok=True)
        unique_name = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join("static", "images", unique_name)

        with open(file_path, "wb") as f:
            f.write(await image.read())
        image_url = f"/static/images/{unique_name}"

    # Create the post with all fields
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

    # Handle tags (if provided)
    if tags:
        for tag_info in tags:
            if isinstance(tag_info, dict):
                label = tag_info.get("label")
                wikidata_url = tag_info.get("wikidata_url")
                description = tag_info.get("description")
            else:  # Treat it as a string if not a dictionary
                label = tag_info
                wikidata_url = "https://www.wikidata.org"  # Default URL
                description = "No description available"

            # Check if tag already exists
            existing_tag = db.query(Tag).filter(Tag.label == label).first()

            if not existing_tag:
                # Create new tag if it doesn't exist
                new_tag = Tag(
                    label=label, wikidata_url=wikidata_url, description=description
                )
                db.add(new_tag)
                db.commit()
                db.refresh(new_tag)
                tag_object = new_tag
            else:
                tag_object = existing_tag

            # Associate tag with post
            db_post.tags.append(tag_object)

    # Save post to database
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    # Return post with creator and all fields
    return {
        "id": db_post.id,
        "title": db_post.title,
        "description": db_post.description,
        "material": db_post.material,
        "length": db_post.length,
        "width": db_post.width,
        "height": db_post.height,
        "color": db_post.color,
        "shape": db_post.shape,
        "weight": db_post.weight,
        "location": db_post.location,
        "smell": db_post.smell,
        "taste": db_post.taste,
        "origin": db_post.origin,
        "image_url": db_post.image_url,
        "creator": current_user.username,
        "interest_count": 0,
        "tags": [
            {
                "label": tag.label,
                "wikidata_url": tag.wikidata_url,
                "description": tag.description,
            }
            for tag in db_post.tags
        ],
    }


@router.get("/posts", response_model=List[PostWithTags])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(PostModel).options(joinedload(PostModel.owner)).all()

    # Serialize posts
    serialized_posts = []
    for post in posts:
        serialized_posts.append(
            {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "image_url": post.image_url,
                "material": post.material,
                "length": post.length,
                "width": post.width,
                "height": post.height,
                "color": post.color,
                "shape": post.shape,
                "weight": post.weight,
                "location": post.location,
                "smell": post.smell,
                "taste": post.taste,
                "origin": post.origin,
                "resolved": False,  # Default to unresolved
                "creator": post.owner.username,
                "interest_count": len(post.interests),
                "tags": [
                    {
                        "label": tag.label,
                        "wikidata_url": tag.wikidata_url,
                        "description": tag.description,
                    }
                    for tag in post.tags
                ],
            }
        )
    return serialized_posts


@router.get("/posts/hot", response_model=List[PostWithTags])
def get_hot_posts(db: Session = Depends(get_db)):
    """
    Fetch posts ordered by interest count in descending order.
    """
    # Subquery for interest count
    interest_count_subquery = (
        db.query(
            PostInterest.post_id, func.count(PostInterest.id).label("interest_count")
        )
        .group_by(PostInterest.post_id)
        .subquery()
    )

    # Query posts with the interest count and the owner's username
    posts = (
        db.query(
            PostModel,
            User.username.label("creator"),
            func.coalesce(interest_count_subquery.c.interest_count, 0).label(
                "interest_count"
            ),
        )
        .outerjoin(
            interest_count_subquery, interest_count_subquery.c.post_id == PostModel.id
        )
        .outerjoin(User, User.id == PostModel.owner_id)
        .order_by(desc("interest_count"))
        .all()
    )

    # Convert query results to the response model
    result = []
    for post, creator, interest_count in posts:
        post_data = post.__dict__.copy()
        post_data["creator"] = creator
        post_data["interest_count"] = interest_count

        # Serialize tags
        post_data["tags"] = [
            {
                "label": tag.label,
                "wikidata_url": tag.wikidata_url,
                "description": tag.description,
            }
            for tag in post.tags
        ]

        result.append(post_data)

    return result


@router.get("/posts/search", response_model=List[PostWithTags])
def search_posts(query: str, db: Session = Depends(get_db)):
    """
    Search posts based on query string. Matches title and description.
    """
    if not query:
        return []

    # Fetch posts and join with User table to get creator username
    posts = (
        db.query(PostModel, User.username.label("creator"))
        .join(User, User.id == PostModel.owner_id)
        .filter(
            or_(
                PostModel.title.ilike(f"%{query}%"),
                PostModel.description.ilike(f"%{query}%"),
            )
        )
        .all()
    )

    # Serialize the results to match PostWithTags schema
    result = []
    for post, creator in posts:
        post_data = post.__dict__.copy()
        post_data["creator"] = creator

        # Serialize tags
        post_data["tags"] = [
            {
                "label": tag.label,
                "wikidata_url": tag.wikidata_url,
                "description": tag.description,
            }
            for tag in post.tags
        ]

        # Calculate interest count
        interest_count = len(post.interests)
        post_data["interest_count"] = interest_count

        result.append(post_data)

    return result


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
    post.creator = post.owner.username
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
