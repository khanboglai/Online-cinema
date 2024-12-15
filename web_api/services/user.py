"""Services with login, register and authentification"""
from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Form, Request, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from config import settings
from exceptions.exceptions import UserIsExistError
from repository.user_dao import ProfileDao, AuthDao
from schemas.user import CreateUserRequest, EditUserRequest
from models.models import Auth, Profile


# !!! SECRET !!!
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

dao = AuthDao()
profile_dao = ProfileDao()

async def register_user(create_user_request: CreateUserRequest = Form()) -> str:
    """Foo for creating new user"""
    username = create_user_request.username
    existing_user = await dao.find_by_username(username)
    if existing_user:
        raise UserIsExistError()  # Update in nearest future
    await dao.add(
        login=username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role='ROLE_USER',
    )
    user = await dao.find_by_username(username)
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

def get_age(birth_date: datetime) -> int:
    '''
    Get user age
    :param birth_date:
    :return:
    '''
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

# async def check_username_available(username: str) -> bool:
#     '''
#     Check if the username is available.
#     :param username:
#     :return:
#     '''
#     user = await dao.find_by_username(username)
#     if user is None:
#         return True
#     return False

async def edit_user(user: UserDependency, form: EditUserRequest) -> Profile:
    '''
    Edit user info
    :param user:
    :param form:
    :return:
    '''
    # if form.username != user.username and await check_username_available(form.username):
    #     user.username = form.username
    # if form.new_password:
    #     user.hashed_password = bcrypt_context.hash(form.new_password)

    # Находим данные юзера в таблице profile
    profile = await profile_dao.find_by_auth_id(user.id)
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

    await profile_dao.update(profile)

    return user
