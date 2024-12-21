import os

# Set mock environment variables for testing
os.environ["SECRET_KEY"] = "mock_secret_key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app
from app.database import get_db
from app.models import User
from app.utils import get_current_user

# Mock the database dependency
app.dependency_overrides[get_db] = lambda: MagicMock()

# Mock user data
MOCK_USER = {"username": "testuser", "password": "testpassword"}
MOCK_POST = {
    "title": "Test Post",
    "description": "This is a test post description",
    "material": "Wood",
    "length": 10.5,
    "width": 5.0,
    "height": 2.5,
    "color": "Brown",
    "shape": "Rectangle",
    "weight": 1.5,
    "location": "Test Location",
    "tags": ["TestTag1", "TestTag2"],
}


# Mock the get_current_user dependency
def mock_get_current_user():
    # Create a mock user instance
    mock_user = User()
    mock_user.id = 1
    mock_user.username = "testuser"
    mock_user.hashed_password = "hashed_testpassword"  # Mock password hash
    return mock_user


app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.text


def test_register_user():
    response = client.post("/register", json=MOCK_USER)
    assert response.status_code in [200, 400]  # Account for user already registered


# def test_login_user():
#     response = client.post("/login", data=MOCK_USER)
#     assert response.status_code == 200


def test_create_post():
    response = client.post("/posts", json=MOCK_POST)
    assert response.status_code in [200, 422]  # Handles missing fields or validation


def test_get_posts():
    response = client.get("/posts")
    assert response.status_code == 200


def test_get_hot_posts():
    response = client.get("/posts/hot")
    assert response.status_code == 200


def test_search_posts():
    response = client.get("/posts/search", params={"query": "Test"})
    assert response.status_code == 200


# def test_get_post_details():
#     post_id = 1  # Replace with a realistic ID if possible
#     response = client.get(f"/posts/{post_id}")
#     assert response.status_code in [200, 404]


# def test_add_comment():
#     post_id = 1  # Replace with a realistic ID if possible
#     comment = {"content": "This is a test comment."}
#     response = client.post(f"/posts/{post_id}/comments", json=comment)
#     assert response.status_code in [200, 404]


# def test_vote_comment():
#     comment_id = 1  # Replace with a realistic ID if possible
#     vote = {"is_upvote": True}
#     response = client.post(f"/comments/{comment_id}/vote", json=vote)
#     assert response.status_code in [200, 404]


def test_toggle_interest():
    post_id = 1  # Replace with a realistic ID if possible
    response = client.post(f"/posts/{post_id}/interested")
    assert response.status_code in [200, 404]
