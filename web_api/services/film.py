"""
Service layer for films.
"""

import os

import aiofiles
from fastapi import UploadFile, Form

from repository.film_dao import FilmDao

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

dao = FilmDao()

async def save_film(
        film_name: str,
        age_rating: int,
        # director: str,
        year: int,
        country: str,
        file: UploadFile):
    '''
    Service for saving films into storage
    :param file:
    :param upload_form:
    :return:
    '''

    print("Save film")

    film = await dao.add(
        name=film_name,
        age_rating=age_rating,
        # director=[director],
        year=year,
        country=country,
    )

    print("film added: " + film_name)

    file_location = os.path.join(UPLOAD_FOLDER, str(film.id) + "_" + film.name + ".mp4")

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

async def get_film_by_id(film_id: int):
    film = await dao.find_by_id(film_id)
    # Пока что не может быть, чтобы не было такого фильма, так как он берется из хранилки эластика
    return film
