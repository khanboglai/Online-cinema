""" Schemas of film """
from pydantic import BaseModel
from fastapi import UploadFile, File


class SaveFilmRequest(BaseModel):
    """ Schema for save film request """
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
    """ Schema for uploading film from frontend """
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
    """ Schema for edit film data form """
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
