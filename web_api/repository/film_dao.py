"""
FilmDao. Dao for Film.
"""

from models.models import Film
from repository.base_dao import BaseDao
from repository.database import async_session_maker


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


