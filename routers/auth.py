"""Routers with login, register and authentification"""
from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Form, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from config import settings
from repository.database import SessionLocal
from schemas.user import User, CreateUserRequest

router = APIRouter(
    prefix='',
    tags=['auth']
)

# !!! SECRET !!!
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_db():
    """Setting connection with database"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBDependency = Annotated[Session, Depends(get_db)]

@router.post("/register")
async def create_user(response: Response,
                      db: DBDependency,
                      create_user_request: CreateUserRequest = Form()):
    """Foo for creating new user"""
    username = create_user_request.username
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with the same login already exists') # Update in nearest future
    create_user_model = User(
        username=username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()
    user = db.query(User).filter(User.username == username).first()
    access_token = create_access_token(user.username,
                                        user.id)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response

@router.post("/login")
async def login(response: Response,
                db: DBDependency,
                create_user_request: CreateUserRequest = Form()):
    """Foo for login user"""
    user = authentificate_user(
        create_user_request.username,
        create_user_request.password,
        db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.') # Update in nearest future
    access_token = create_access_token(user.username,
                                       user.id)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response

@router.post('/logout')
async def logout(request: Request):
    """Foo for logout user"""
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='access_token')
    return response

def authentificate_user(username: str, password: str, db):
    """Auth user with his hashed password"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: str):
    """Creation of JWT token"""
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + timedelta(hours=1)
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(db: DBDependency,
                           request: Request) -> User | None:
    """Getting user info by JWT token"""
    token = request.cookies.get('access_token')
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user = db.execute(select(User).filter_by(username=username)).scalar_one_or_none()
        return user
    except JWTError as e:
        return None
