from pydantic import BaseModel, field_validator
from typing import Optional, List


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    label: str
    wikidata_url: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PostBase(BaseModel):
    title: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    material: Optional[str] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    color: Optional[str] = None
    shape: Optional[str] = None
    weight: Optional[float] = None
    location: Optional[str] = None
    smell: Optional[str] = None
    taste: Optional[str] = None
    origin: Optional[str] = None
    tags: Optional[List[TagBase]] = []

    @field_validator("length", "width", "height", "weight")
    def check_positive(cls, v, field):
        if v is not None and v < 0:
            raise ValueError(f"{field.name} must be greater than 0")
        return v


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class CommentUser(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentWithScore(CommentBase):
    id: int
    post_id: int
    user_id: int
    score: int
    user: CommentUser  # Include user data

    class Config:
        from_attributes = True


class CommentVoteCreate(BaseModel):
    is_upvote: bool


class PostWithComments(Post):
    comments: List[CommentWithScore] = []


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True


class PostWithTags(PostBase):
    id: int
    tags: List[Tag] = []

    class Config:
        from_attributes = True


class PostWithDetails(PostBase):
    id: int
    owner_id: int
    comments: List[CommentWithScore] = []  # Include comments
    tags: List[Tag] = []  # Include tags

    class Config:
        from_attributes = True
