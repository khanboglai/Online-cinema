"""Services with login, register and authentification"""
from datetime import timedelta, datetime, timezone
from math import floor
from typing import Annotated
from sqlalchemy.exc import IntegrityError

from fastapi import Form, Request, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from config import settings
from exceptions.exceptions import UserIsExistError, UserEmailExistError
from repository.interaction_dao import InteractionDao
from repository.subscription_dao import SubscriptionDao
from repository.user_dao import ProfileDao, AuthDao
from schemas.user import CreateUserRequest, EditUserRequest, ChangeUserSubscription
from models.models import Auth, Profile, Interaction, Film, Subscription
from services.search import delete_user_from_es, add_user_to_es, update_user_in_es

# !!! SECRET !!!
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
SUBSCRIPTION_DURATION = timedelta(days=30)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

dao = AuthDao()
profile_dao = ProfileDao()
interaction_dao = InteractionDao()
subscription_dao = SubscriptionDao()

async def register_user(create_user_request: CreateUserRequest = Form()) -> str:
    """Foo for creating new user"""
    username = create_user_request.username
    # existing_user = await dao.find_by_username(username)
    # if existing_user:
    #     raise UserIsExistError()  # Update in nearest future
    try:
        await dao.add(
            login=username,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            role='ROLE_USER',
        )
    except IntegrityError:
        raise UserIsExistError()
    
    user = await dao.find_by_username(username)
    # Добавление записи о юзере в эластик
    await add_user_to_es(user.id, user.login)
    # Создаем новый профиль в таблице profile
    await profile_dao.add(auth_id=user.id)
    access_token = create_access_token(user.login,
                                       user.id)

    return access_token

# async def get_username_from_auth()

async def authenticate_user(username: str, password: str) -> Auth | None:
    """Auth user with his hashed password"""
    user = await dao.find_by_username(username)
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: str):
    """Creation of JWT token"""
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + timedelta(hours=1)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request) -> Auth | None:
    """Getting user info by JWT token"""
    token = request.cookies.get('access_token')
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user = await dao.find_by_username(username)
        return user
    except JWTError as e:
        return None

UserDependency = Annotated[Auth, Depends(get_current_user)]

def get_age(birth_date: datetime | None) -> int | None:
    '''
    Get user age
    :param birth_date:
    :return:
    '''
    if birth_date is None:
        return None

    return (
            datetime.now().year
            - birth_date.year
            - (
                    (datetime.now().month, datetime.now().day)
                    < (birth_date.month, birth_date.day)
            )
    )

async def get_birth_date_by_user_id(user: UserDependency):
    # Находим данные юзера в таблице profile
    profile = await profile_dao.find_by_auth_id(user.id)
    if profile.birth_date:
        return profile.birth_date
    return None

async def get_name_by_user_id(user: UserDependency):
    # Находим данные юзера в таблице profile
    profile = await profile_dao.find_by_auth_id(user.id)
    if profile.name:
        return profile.name
    return None

async def get_surname_by_user_id(user: UserDependency):
    # Находим данные юзера в таблице profile
    profile = await profile_dao.find_by_auth_id(user.id)
    if profile.surname:
        return profile.surname
    return None

async def get_email_by_user_id(user: UserDependency):
    # Находим данные юзера в таблице profile
    profile = await profile_dao.find_by_auth_id(user.id)
    if profile.email:
        return profile.email
    return None

async def get_profile_by_user_id(id: int):
    # Получаем весь Profile в таблице profile
    return await profile_dao.find_by_auth_id(id)

async def get_general_watchtime_by_user_id(id: int) -> int:
    # Получаем общее количество просмотренных часов
    interactions = await interaction_dao.get_all_interactions_by_user(id)

    watchtime = 0

    for interaction in interactions:
        if interaction is not None:
            watchtime += interaction.watchtime

    return watchtime

async def get_recently_watched(id: int, n: int) -> list[(Interaction, Film)]:
    recently_watched = await profile_dao.get_recently_watched(id, n)

    for (interaction, film) in recently_watched:
        last_interaction = interaction.last_interaction.replace(tzinfo=timezone.utc)
        delta = (datetime.now(timezone.utc) - last_interaction).total_seconds()

        if delta / 3600 >= 1:
            delta_str = str(floor(delta / 3600)) + ' hour'
            if delta_str != '1 hour':
                delta_str += 's'
        elif delta / 60 >= 1:
            delta_str = str(floor(delta / 60)) + ' minute'
            if delta_str != '1 minute':
                delta_str += 's'
        else:
            delta_str = str(floor(delta)) + ' second'
            if delta_str != '1 second':
                delta_str += 's'

        interaction.last_interaction = delta_str

    return recently_watched


async def edit_user(user: UserDependency, form: EditUserRequest) -> Auth:
    '''
    Edit user info
    :param user:
    :param form:
    :return:
    '''

    # Изменяем данные пользователя в таблице profile и auth
    profile = await profile_dao.find_by_auth_id(user.id)
    if form.login:
        user.login = form.login
        await update_user_in_es(form.login, user.id)
    if form.new_password:
        user.hashed_password = bcrypt_context.hash(form.new_password)
    if form.name:
        profile.name = form.name
    if form.surname:
        profile.surname = form.surname
    if form.birth_date:
        profile.birth_date = form.birth_date
    if form.sex:
        profile.sex = form.sex
    if form.email:
        profile.email = form.email

    try:
        await dao.update(user)
    except IntegrityError:
        raise UserIsExistError()
    
    try:
        await profile_dao.update(profile)
    except IntegrityError:
        raise UserEmailExistError()

    return user

async def delete_user(user_id):
    await dao.delete_by_auth_id(user_id)
    await delete_user_from_es(user_id)

def check_subscription(subscription: Subscription) -> bool:
    if subscription is None:
        return False
    if subscription.started_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        return False
    if subscription.finished_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return False
    return True

async def change_subscription(subscription: ChangeUserSubscription):
    if not subscription.set_to:
        await subscription_dao.delete_subscription(subscription.user_id)
        return
    started_at = datetime.now()
    finished_at = started_at + SUBSCRIPTION_DURATION

    current_sub = await subscription_dao.get_subscription_by_id(subscription.user_id)
    if current_sub is None:
        await subscription_dao.create_subscription(subscription.user_id, started_at, finished_at)
    else:
        await subscription_dao.update_subscription(subscription.user_id, started_at, finished_at)

async def get_subscription(id: int) -> Subscription:
    return await subscription_dao.get_subscription_by_id(id)
