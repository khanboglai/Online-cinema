""" Service layer for films. """

import os
import logging
import aiofiles
import boto3.exceptions
from fastapi import UploadFile, Form
import boto3
from repository.film_dao import FilmDao


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# тестово
# засунуть это в один файл
s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000',
    aws_access_key_id='storage',
    aws_secret_access_key='qwerty2024',
)

BUCKET_NAME = 'storage-cinema'

# засунуть это в главный файл при запуске приложения создавать
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    logger.warning(f"S3: {e}")


dao = FilmDao()

async def save_film(
        film_name: str,
        age_rating: int,
        # director: str,
        year: int,
        # country: str, # исправить говно
        file: UploadFile):
    '''
    Service for saving films into storage
    :param file:
    :param upload_form:
    :return:
    '''

    logger.info("Save film")

    film = await dao.add(
        name=film_name,
        age_rating=age_rating,
        # director=[director],
        year=year,
        # country=country,
    )

    logger.info(f"film added: {film_name}")

    file_location = os.path.join(UPLOAD_FOLDER, str(film.id) + "_" + film.name + ".mp4")

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
        logger.info("File created in directory upload")

    # ДОБАВИТЬ ЗАГРУЗКУ ОБЛОЖКИ ФИЛЬМА

    try:
        # загрузка файла (фильма) в s3 
        s3_client.upload_file(file_location, BUCKET_NAME, f"{film.id}/{film.name}.mp4")
        # удаление файла с сервера
        os.remove(file_location)

        logger.info("Uploaded file and removed from uploads")
    except boto3.exceptions as e:
        logger.error(f"Problems: {e}")


async def get_film_by_id(film_id: int):
    film = await dao.find_by_id(film_id)
    # Пока что не может быть, чтобы не было такого фильма, так как он берется из хранилки эластика
    return film
