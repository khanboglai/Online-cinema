"""
FilmDao. Dao for Film.
"""

from models.models import Film
from repository.base_dao import BaseDao
from repository.database import async_session_maker
from sqlalchemy import select, delete, update

from schemas.film import EditFilmForm


class FilmDao(BaseDao):
    model = Film

    @classmethod
    async def get_by_film_name(cls, name):
        '''
        Get films by name
        :param name:
        :return:
        '''
        async with async_session_maker() as session:
            query = session.query(Film).filter_by(name=name)
            result = await session.execute()
            return result.scalars().all()
        
    @classmethod
    async def udate_film_rate(cls, film):
        data_to_update = vars(film).copy()
        data_to_update.pop('id', None)

        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id = film.id)
            )

            result = (await session.execute(query)).scalar_one()
            result.rating_kp = film.rating_kp
            await session.commit()

    @classmethod
    async def find_newest_films(cls):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .order_by(cls.model.year.desc())
                .limit(9)
            )

            result = (await session.execute(query)).scalars().all()
            return result

    @classmethod
    async def update_film(cls, film: EditFilmForm) -> None:
        directors_array = [item.strip() for item in film.director.split(',')]
        countries_array = [item.strip() for item in film.country.split(',')]
        actors_array = [item.strip() for item in film.actor.split(',')]
        genres_array = [item.strip() for item in film.genre.split(',')]
        tags_array = [item.strip() for item in film.tags.split(',')]
        async with async_session_maker() as session:
            query = (
                update(Film).where(Film.id == film.id).values(
                    name = film.film_name,
                    description = film.description,
                    directors = directors_array,
                    actors = actors_array,
                    genres = genres_array,
                    year = film.year,
                    countries = countries_array,
                    studios = film.studios,
                    tags = tags_array,
                    age_rating = film.age_rating,
                )
            )

            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_film_by_id(cls, film_id: int):
        async with async_session_maker() as session:
            query = (
                delete(cls.model)
                .filter_by(id = film_id)
            )
            await session.execute(query)
            await session.commit()
