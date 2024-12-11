"""
BaseDao class. It is parent of every dao.
A class used for interacting with the database.
"""

from repository.database import async_session_maker
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


class BaseDao:
    model = None

    @classmethod
    async def find_by_id(cls, id: int):
        '''
        Find record by id
        :param id:
        :return:
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls):
        '''
        Get all records
        :return:
        '''
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        '''
        Find record by some filters
        :param filter_by:
        :return:
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **values):
        '''
        Add record
        :param values:
        :return:
        '''

        async with async_session_maker() as session:
            async with session.begin():
                print('basedao add')
                new_instance = cls.model(**values)
                session.add(new_instance)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                print("add successful")
                return new_instance
