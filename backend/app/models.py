from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Float,
    JSON,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from sqlalchemy.sql import func
from sqlalchemy import DateTime

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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    posts = relationship("Post", back_populates="owner")


post_tag_table = Table(
    "post_tag",
    Base.metadata,
    Column(
        "post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class PostInterest(Base):
    __tablename__ = "post_interests"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    post = relationship("Post", back_populates="interests")
    user = relationship("User")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    wikidata_url = Column(String, nullable=True)
    description = Column(String, nullable=True)

    # Relationship with posts
    posts = relationship("Post", secondary=post_tag_table, back_populates="tags")


class Post(Base):
    __tablename__ = "posts"
    __allow_unmapped__ = True
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=False)
    material = Column(String, nullable=True)
    length = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    color = Column(String, nullable=True)
    shape = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    smell = Column(String, nullable=True)
    taste = Column(String, nullable=True)
    origin = Column(String, nullable=True)
    tags = relationship("Tag", secondary=post_tag_table, back_populates="posts")
    interests = relationship(
        "PostInterest", back_populates="post", cascade="all, delete-orphan"
    )

    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )

    @property
    def interest_count(self):
        return len(self.interests)


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

    comment = relationship("Comment", back_populates="votes")
    user = relationship("User")


Base.metadata.create_all(bind=engine)
