from sqlalchemy.future import select

from models.models import Recommend
from repository.base_dao import BaseDao
from repository.database import async_session_maker

class RecommendDao(BaseDao):
    model = Recommend

    @classmethod
    async def get_recommend_by_profile_id(cls, profile_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(profile_id = profile_id)
            )

            result = (await session.execute(query)).scalars().all()
            return result
        