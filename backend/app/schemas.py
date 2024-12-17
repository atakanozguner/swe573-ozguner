from pydantic import BaseModel


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
    content: str


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
