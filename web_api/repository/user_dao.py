"""
UserDao. Dao for User.
"""

from sqlalchemy import update
from sqlalchemy.future import select

from repository.base_dao import BaseDao

from models.models import Auth, Profile, Interaction, Film
from repository.database import async_session_maker

class ProfileDao(BaseDao):
    """Обновление данных для лк"""
    model = Profile

    @classmethod
    async def find_by_auth_id(cls, id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(auth_id=id)
            result = await session.execute(query)
            return result.scalar_one_or_none()


    @classmethod
    async def update(cls, user: Profile):
        '''
        Update user info.
        :param user:
        :return:
        '''
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
            result.name = user.name
            result.surname = user.surname
            result.birth_date = user.birth_date
            result.sex = user.sex
            result.email = user.email
            await session.commit()

    @classmethod
    async def get_recently_watched(cls, id: int, n: int) -> list[(Interaction, Film)]:
        """
        Get recently watched films by user with id.
        :param id: user id
        :param n: number of films to return
        :return:
        """
        async with async_session_maker() as session:
            query = select(Interaction, Film) \
                .select_from(Profile) \
                .join(Interaction) \
                .join(Film) \
                .where(Interaction.profile_id == id) \
                .order_by(Interaction.last_interaction.desc()) \
                .limit(n)
            result = await session.execute(query)
            return result.all()


class AuthDao(BaseDao):
    """Аутентификация для юзера при логине"""
    model = Auth

    @classmethod
    async def find_by_username(cls, username: str) -> Auth:
        '''
        Find user by username.
        :param username:
        :return:
        '''
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(login=username)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def update(cls, user: Auth):
        '''
        Update user info.
        :param user:
        :return:
        '''
        data_to_update = vars(user).copy()
        data_to_update.pop('id', None)

        async with async_session_maker() as session:
            query = (
                select(cls.model)
                .filter_by(id=user.id)
            )

            result = (await session.execute(query)).scalar_one()
            # for attr, value in data_to_update.items():
            #     setattr(result, attr, value)
            result.login = user.login
            result.hashed_password = user.hashed_password
            await session.commit()
