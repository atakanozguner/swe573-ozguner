from pydantic import BaseModel
from typing import Optional, List


# Schema for creating a new user (registration)
class UserCreate(BaseModel):
    username: str
    password: str


# Schema for returning user data
class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    weight: Optional[str] = None
    location: Optional[str] = None
    smell: Optional[str] = None
    taste: Optional[str] = None
    origin: Optional[str] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int

    class Config:
        from_attributes = True


class CommentVoteCreate(BaseModel):
    is_upvote: bool


class CommentWithScore(Comment):
    score: int


# For returning post details with comments:
class PostWithComments(Post):
    comments: List[Comment] = []
