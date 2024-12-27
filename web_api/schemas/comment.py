""" Schemas for comments """
from pydantic import BaseModel


class Comment(BaseModel):
    """ Comment schema """
    rating: float
    text: str

class CommentRequest(BaseModel):
    """ Comment request schema """
    user_id: int
    rating: float
    text: str
    film_id: int
