from sqlalchemy import update
from sqlalchemy.future import select

from repository.base_dao import BaseDao

from models.user import User
from repository.database import async_session_maker


class UserDao(BaseDao):
    model = User

    @classmethod
    async def find_by_username(cls, username: str) -> User:
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(username=username)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def update(cls, user: User):
        data_to_update = vars(user).copy()
        data_to_update.pop('id', None)

        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id = user.id)
            )

            result = (await session.execute(query)).scalar_one()
            # for attr, value in data_to_update.items():
            #     setattr(result, attr, value)
            result.username = user.username
            result.birth_date = user.birth_date
            result.sex = user.sex
            result.hashed_password = user.hashed_password
            await session.commit()
