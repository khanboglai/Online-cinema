""" Service layer for films. """

import logging
from boto3.exceptions import Boto3Error
from fastapi import UploadFile, Form
from config import s3_client, BUCKET_NAME
from repository.film_dao import FilmDao


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
