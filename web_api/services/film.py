""" Service layer for films. """

import logging
from boto3.exceptions import Boto3Error
from config import s3_client, BUCKET_NAME
from repository.film_dao import FilmDao
from repository.user_dao import ProfileDao
from repository.comment_dao import CommentDao
from services.search import add_document
from schemas.film import SaveFilmRequest
from schemas.comment import CommentRequest


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dao = FilmDao()

user_dao = ProfileDao()
comment_dao = CommentDao()


async def save_film(film_request: SaveFilmRequest):
    '''
    Service for saving films into storage
    :param file:
    :param upload_form:
    :return:
    '''
    directors_array = [item.strip() for item in film_request.director.split(',')]
    countries_array = [item.strip() for item in film_request.country.split(',')]
    actors_array = [item.strip() for item in film_request.actor.split(',')]
    genres_array = [item.strip() for item in film_request.genre.split(',')]
    tags_array = [item.strip() for item in film_request.tags.split(',')]


    logger.info("Save film")

    film = await dao.add(
        name=film_request.film_name,
        age_rating=film_request.age_rating,
        directors=directors_array,
        year=film_request.year,
        countries=countries_array,
        description=film_request.description,
        actors=actors_array,
        genres=genres_array,
        studios=film_request.studios,
        tags=tags_array
    )

    logger.info(f"film added: {film_request.film_name}")

    # добавление записи в эластик
    await add_document(film.name, film.id)

    try:
        # загрузка файла (обожки) в s3
        file_content = await film_request.cover.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{film.id}/image.png",
            Body=file_content,
            ContentLength=len(file_content)
        )

        logger.info("Cover file uploaded successfully")
    except Boto3Error as e:
        logger.error(f"Problems: {e}")

    try:
        # загрузка файла (фильма) в s3 

        file_content = await film_request.file.read()
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=f"{film.id}/video.mp4",
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

async def add_comment_to_db(comment: CommentRequest):
    profile = await user_dao.find_by_auth_id(comment.user_id)

    await comment_dao.add(
        profile_id=profile.id,
        film_id=comment.film_id,
        rating=comment.rating,
        text=comment.text
    )

    new_rate = await comment_dao.get_new_rate(comment.film_id)

    film = await dao.find_by_id(comment.film_id)

    film.rating_kp = new_rate
    
    await dao.udate_film_rate(film)

    logger.info("Comment was added successfully!")

async def get_all_comments(film_id: int):
    comments = await comment_dao.get_all_comments(film_id)
    return comments
