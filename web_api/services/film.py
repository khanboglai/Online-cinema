""" Service layer for films. """

import logging
from boto3.exceptions import Boto3Error
from config import s3_client, BUCKET_NAME
from repository.film_dao import FilmDao
from repository.user_dao import ProfileDao
from repository.comment_dao import CommentDao
from repository.recommend_dao import RecommendDao
from services.search import add_document, update_document, delete_document
from services.user import get_age
from schemas.film import SaveFilmRequest, EditFilmForm
from schemas.comment import CommentRequest
from elasticsearch import ConnectionError
from boto3.exceptions import Boto3Error


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dao = FilmDao()

user_dao = ProfileDao()
comment_dao = CommentDao()
recommend_dao = RecommendDao()


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

    try:
        # добавление записи в эластик
        await add_document(film.name, film.id)
        logger.info(f"film {film.name} added to elastic with id {film.id}")
    # обрабатываем случай когда эластик не запустился, но в остальных случаях он должен отрабатывать всегда
    except ConnectionError as e:
        logger.error(f"Elasticsearch error: {e}")
        await delete_film(film.id)

    
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

async def get_newest_films():
    films = await dao.find_newest_films()
    return films

async def get_recommend_films(user_id: int):
    profile = await user_dao.find_by_auth_id(user_id)

    recs = await recommend_dao.get_recommend_by_profile_id(profile.id)
    if not recs:
        return None
    return recs

async def get_recommended_films_for_new_user(profile_id: int = 0):
    recs = await recommend_dao.get_recommend_by_profile_id(profile_id)
    if not recs:
        return None
    return recs

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

async def edit_film(film: EditFilmForm) -> None:
    await dao.update_film(film)
    await update_document(film.film_name, film.id)

async def delete_film(film_id: int):
    await dao.delete_film_by_id(film_id)
    logger.info(f"Deleted from pg")
    await delete_document(film_id)
    logger.info(f"Deleted from Elastic")
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"{film_id}/image.png")
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"{film_id}/video.mp4")
    logger.info(f"Deleted film with id: {film_id}")

async def check_age(user_id: int, film_id: int):
    profile = await user_dao.find_by_auth_id(user_id)
    film = await dao.find_by_id(film_id)
    if profile.birth_date is None:
        return False
    if get_age(profile.birth_date) < film.age_rating and user_id != 0:
        return False
    return True
