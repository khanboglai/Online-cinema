"""
Service layer for films.
"""

import os

import aiofiles
from fastapi import UploadFile, Form
import boto3
from repository.film_dao import FilmDao

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000',
    aws_access_key_id='storage',  # Замените на ваш Access Key
    aws_secret_access_key='qwerty2024',  # Замените на ваш Secret Key
)

BUCKET_NAME = 'storage-cinema'
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    # logger.warning(f"S3: {e}")
    print(f"S3: {e}") # потом исправить


dao = FilmDao()

async def save_film(
        film_name: str,
        age_rating: int,
        # director: str,
        year: int,
        # country: str,
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
        # country=country,
    )

    print("film added: " + film_name)

    file_location = os.path.join(UPLOAD_FOLDER, str(film.id) + "_" + film.name + ".mp4")

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    s3_client.upload_file(file_location, BUCKET_NAME, f"{film.id}/{film.name}.mp4")

async def get_film_by_id(film_id: int):
    film = await dao.find_by_id(film_id)
    # Пока что не может быть, чтобы не было такого фильма, так как он берется из хранилки эластика
    return film
