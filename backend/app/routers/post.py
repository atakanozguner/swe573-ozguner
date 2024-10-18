from fastapi import APIRouter

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def get_posts():
    return {"message": "Mock Response: List of posts"}
