from typing import List

from sqlalchemy.future import select

from datetime import datetime

from models.models import Interaction
from repository.base_dao import BaseDao
from repository.database import async_session_maker


class InteractionDao(BaseDao):
    model = Interaction
    
    @classmethod
    async def get_interaction_by_user_and_film(cls, user_id, film_id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(profile_id=user_id, film_id=film_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_interactions_by_user(cls, user_id) -> List[Interaction]:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(profile_id=user_id)
            result = await session.execute(query)
            return result.scalars().all()
        
    @classmethod
    async def update(cls, interaction: Interaction):
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