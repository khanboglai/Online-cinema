""" Service layer for films. """

import os
import logging
import aiofiles
from boto3.exceptions import Boto3Error
from fastapi import UploadFile, Form
import boto3
from boto3.s3.transfer import TransferConfig
from repository.film_dao import FilmDao


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# UPLOAD_FOLDER = "/app/uploads"
# os.makedirs(UPLOAD_FOLDER, mode=0o777, exist_ok=True)


# тестово
# засунуть это в один файл
s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000',
    aws_access_key_id='storage',
    aws_secret_access_key='qwerty2024',
)

BUCKET_NAME = 'storage-cinema'

# # Настройка конфигурации для многочастной загрузки
# config = TransferConfig(
#     multipart_threshold=1024 * 25,  # Порог для многочастной загрузки (25 МБ)
#     max_concurrency=10,              # Максимальное количество параллельных загрузок
#     multipart_chunksize=1024 * 25,   # Размер частей (25 МБ)
#     use_threads=True                  # Использовать потоки
# )

# засунуть это в главный файл при запуске приложения создавать
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    logger.warning(f"S3: {e}")


dao = FilmDao()

async def save_film(
        film_name: str,
        age_rating: int,
        director: str,
        year: int,
        country: str,
        description: str,
        actor: str,
        genre: str,
        studios: str,
        tags: str,
        file: UploadFile,
        cover: UploadFile):
    '''
    Service for saving films into storage
    :param file:
    :param upload_form:
    :return:
    '''

    directors_array = [item.strip() for item in director.split(',')]
    countries_array = [item.strip() for item in country.split(',')]
    actors_array = [item.strip() for item in actor.split(',')]
    genres_array = [item.strip() for item in genre.split(',')]
    tags_array = [item.strip() for item in tags.split(',')]


    logger.info("Save film")

    film = await dao.add(
        name=film_name,
        age_rating=age_rating,
        directors=directors_array,
        year=year,
        countries=countries_array,
        description=description,
        actors=actors_array,
        genres=genres_array,
        studios=studios,
        tags=tags_array
    )

    logger.info(f"film added: {film_name}")


    try:
        # загрузка файла (обожки) в s3
        file_content = await cover.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{film.id}/{film.name}.png",
            Body=file_content,
            ContentLength=len(file_content)
        )

        logger.info("Cover file uploaded successfully")
    except Boto3Error as e:
        logger.error(f"Problems: {e}")

    try:
        # загрузка файла (фильма) в s3 

        file_content = await file.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{film.id}/{film.name}.mp4",
            Body=file_content,
            ContentLength=len(file_content)
        )
        logger.info("Film file uploaded successfully")
    except Boto3Error as e:
        logger.error(f"Problems: {e}")


async def get_film_by_id(film_id: int):
    film = await dao.find_by_id(film_id)
    # Пока что не может быть, чтобы не было такого фильма, так как он берется из хранилки эластика
    return film
