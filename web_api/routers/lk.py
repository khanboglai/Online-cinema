from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from config import templates
from logs import logger
from exceptions.exceptions import UserIsExistError, UserEmailExistError
from schemas.user import EditUserRequest
from services.user import UserDependency, edit_user, create_access_token, get_birth_date_by_user_id, \
    get_name_by_user_id, get_surname_by_user_id, get_email_by_user_id, get_profile_by_user_id, get_age, \
    get_general_watchtime_by_user_id, get_recently_watched


router = APIRouter(prefix="/lk", tags=["Personal Account"])

@router.get("/")
async def get_lk_html(user: UserDependency,
                      request: Request):
    """Personal account page"""
    if user is None:
        return RedirectResponse(url="/login")
    profile = await get_profile_by_user_id(user.id)
    watchtime = await get_general_watchtime_by_user_id(user.id)
    number_of_recently_watched = 5
    recently_watched = await get_recently_watched(user.id, number_of_recently_watched)

    # TODO: recently watched
    return templates.TemplateResponse(
        "lk.html",
        {
            "profile": profile,
            "age": get_age(profile.birth_date),
            "watchtime": watchtime,
            "recently_watched": recently_watched,
            "request": request
        }
    )

@router.get("/edit")
async def get_edit_html(user: UserDependency,
                        request: Request):
    if user is None:
        return RedirectResponse(url="/login")
    """Personal account edit page"""
    profile = await get_profile_by_user_id(user.id)
    # name: str | None = await get_name_by_user_id(user)
    # surname: str | None = await get_surname_by_user_id(user)
    # birth_date: datetime | None = await get_birth_date_by_user_id(user)
    # email: str | None = await get_email_by_user_id(user)
    return templates.TemplateResponse(
        "edit_lk.html",
        {
            "request": request,
            "profile": profile,
            "auth": user
        }
    )

@router.post("/edit")
async def edit(response: Response,
               user: UserDependency,
               form: EditUserRequest = Form()):
    try:
        new_user = await edit_user(user, form)
    except UserIsExistError as e:
        logger.error(e)
        return JSONResponse(status_code=401, content={"error": e.message})
    except UserEmailExistError as e:
        logger.error(e)
        return JSONResponse(status_code=401, content={"error": e.message})
    access_token = create_access_token(new_user.login,
                                       new_user.id)
    response = RedirectResponse(url="/lk", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response
