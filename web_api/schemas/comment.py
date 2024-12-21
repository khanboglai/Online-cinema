from pydantic import BaseModel

class Comment(BaseModel):
    rating: float
    text: str

class CommentRequest(BaseModel):
    user_id: int
    rating: float
    text: str
    film_id: int
