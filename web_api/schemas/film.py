""" Schema of film """

from pydantic import BaseModel
from fastapi import UploadFile, File, Form

class SaveFilmRequest(BaseModel):
    film_name: str
    age_rating: int
    director: str
    year: int
    country: str
    description: str
    actor: str
    genre: str
    studios: str
    tags: str
    file: UploadFile
    cover: UploadFile

class UploadFilmForm(BaseModel):
    film_name: str
    age_rating: int
    director: str
    year: int
    country: str
    description: str
    actor: str
    genre: str
    studios: str
    tags: str
    file: UploadFile = File(...)
    cover: UploadFile = File(...)

class EditFilmForm(BaseModel):
    id: int
    film_name: str
    age_rating: int
    director: str
    year: int
    country: str
    description: str
    actor: str
    genre: str
    studios: str
    tags: str
