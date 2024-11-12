from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from repository.database import SessionLocal
from models.models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# !!! SECRET !!!
SECRET_KEY = 'z9t9w6dluej8fupds3fvefoozz6wlymglropksbavn32ehin9lclertyweco4rhri2weg1r3s0x4024yup42ufg4rgt6830tbfvm'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oath2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# сюда шаблон
@router.post("/register")
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    username = create_user_request.username
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with the same login already exists')
    create_user_model = User(
        username=username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )
    db.add(create_user_model)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# сюда шаблон
@router.post("/login")
async def login(db: db_dependency,
                create_user_request: CreateUserRequest):
    user = authentificate_user(create_user_request.username, create_user_request.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# сюда не надо шаблон, тут для бэка все
@router.post("/token", response_model=Token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authentificate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

def authentificate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

