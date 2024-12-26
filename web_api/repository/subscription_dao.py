from datetime import datetime

from sqlalchemy import select, DateTime, insert, delete, update

from models.models import Subscription
from repository.base_dao import BaseDao
from repository.database import async_session_maker


class SubscriptionDao(BaseDao):
    model = Subscription

    @classmethod
    async def get_subscription_by_id(cls, id: int) -> Subscription | None:
        async with async_session_maker() as session:
            query = (
                select(Subscription).where(Subscription.id == id)
            )

            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def create_subscription(cls, id: int, started_at: datetime, finished_at: datetime) -> None:
        async with async_session_maker() as session:
            query = (
                insert(Subscription).values(id=id, started_at=started_at, finished_at=finished_at)
            )

            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_subscription(cls, id: int) -> None:
        async with async_session_maker() as session:
            query = (
                delete(Subscription).where(Subscription.id == id)
            )

            await session.execute(query)
            await session.commit()

    @classmethod
    async def update_subscription(cls, id: int, started_at: datetime, finished_at: datetime) -> None:
        async with async_session_maker() as session:
            query = (
                update(Subscription).where(Subscription.id == id).values(started_at=started_at, finished_at=finished_at)
            )

            await session.execute(query)
            await session.commit()
