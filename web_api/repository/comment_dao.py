""" DAO for table reply """
from sqlalchemy import select, func

from models.models import Reply, Profile
from repository.base_dao import BaseDao
from repository.database import async_session_maker


class CommentDao(BaseDao):
    """ Data Access Object class for table reply """
    model = Reply


    @classmethod
    async def get_new_rate(cls, film_id: int):
        """ Method for getting new rate for film by comments """
        async with async_session_maker() as session:
            query = (
                select(func.avg(cls.model.rating))
                .filter_by(film_id = film_id)
            )

            result = (await session.execute(query)).scalar_one()
            return result
        
    @classmethod
    async def get_all_comments(cls, film_id: int):
        """ Method for getting all comments for film """
        async with async_session_maker() as session:
            query = (
                select(Profile.name, Profile.surname, Reply.rating, Reply.text)
                .join(Profile)
                .filter(Reply.film_id == film_id)
            )
            result = (await session.execute(query)).all()
            return result
        