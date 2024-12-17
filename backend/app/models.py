from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime


# Database setup
try:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

except ValueError as e:
    print(f"Error: {e}")
    raise SystemExit(e)


# Define User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    material = Column(String, nullable=True)
    size = Column(String, nullable=True)
    color = Column(String, nullable=True)
    shape = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    location = Column(String, nullable=True)
    smell = Column(String, nullable=True)
    taste = Column(String, nullable=True)
    origin = Column(String, nullable=True)

    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    post = relationship("Post", back_populates="comments")
    user = relationship("User")
    votes = relationship(
        "CommentVote", back_populates="comment", cascade="all, delete-orphan"
    )


class CommentVote(Base):
    __tablename__ = "comment_votes"

    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_upvote = Column(Boolean, nullable=False)

    # Relationships if needed
    comment = relationship("Comment", back_populates="votes")
    user = relationship("User")


# Create the tables in the database if they don't exist
Base.metadata.create_all(bind=engine)
