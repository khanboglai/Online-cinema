"""Routers with login, register and authentification"""
from datetime import timedelta, datetime
from fastapi import APIRouter, HTTPException, Form, Response, Request
from fastapi.responses import RedirectResponse
from starlette import status

from config import templates
from exceptions.exceptions import UserIsExistError
from schemas.user import CreateUserRequest
from services.user import register_user, authenticate_user, create_access_token, UserDependency
from logs import logger


router = APIRouter(prefix='', tags=['auth'])


@router.get("/login")
async def get_login_html(user: UserDependency, request: Request):
    """Returns template for login page"""
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request})
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.get("/register")
async def get_register_html(user: UserDependency, request: Request):
    """Returns template for register page"""
    if user is None:
        return templates.TemplateResponse("register.html", {"request": request})
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@router.post("/register")
async def create_user(response: Response,
                      create_user_request: CreateUserRequest = Form()):
    """Foo for creating new user"""
    try:
        access_token = await register_user(create_user_request)
    except UserIsExistError as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='User with the same login already exists')

    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response


@router.post("/login")
async def login(response: Response,
                create_user_request: CreateUserRequest = Form()):
    """Foo for login user"""
    user = await authenticate_user(
        create_user_request.username,
        create_user_request.password
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.') # Update in nearest future
    access_token = create_access_token(user.login,
                                       user.id)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response


@router.get('/logout')
async def logout(request: Request, user: UserDependency):
    """Foo for logout user"""
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='access_token')
    logger.info(f"Logouted user: {user.login}")
    return response
