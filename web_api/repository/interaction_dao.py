""" DAO for table interaction """
from typing import List
from sqlalchemy.future import select
from datetime import datetime

from models.models import Interaction
from repository.base_dao import BaseDao
from repository.database import async_session_maker


class InteractionDao(BaseDao):
    """ Data Access Object class for table interaction """
    model = Interaction
    

    @classmethod
    async def get_interaction_by_user_and_film(cls, user_id, film_id):
        """ Method for getting unique interaction by user_id and film_ids"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(profile_id=user_id, film_id=film_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        

    @classmethod
    async def get_all_interactions_by_user(cls, user_id) -> List[Interaction]:
        """ Method for getting all users interaction """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(profile_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()
        
        
    @classmethod
    async def update(cls, interaction: Interaction):
        """ Method for update intaraction info """
        data_to_update = vars(interaction).copy()
        data_to_update.pop('id', None)

        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id = interaction.id)
            )

            result = (await session.execute(query)).scalar_one()
            result.last_interaction = datetime.now()
            result.count_interaction += 1
            await session.commit()


    @classmethod
    async def update_time(cls, interaction: Interaction):
        """ Method for update watchtime in interaction """
        data_to_update = vars(interaction).copy()
        data_to_update.pop('id', None)

        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id = interaction.id)
            )

            result = (await session.execute(query)).scalar_one()
            if result.watchtime is not None and result.watchtime < interaction.watchtime:
                result.watchtime = interaction.watchtime
            if result.watchtime is None:
                result.watchtime = interaction.watchtime
            await session.commit()
