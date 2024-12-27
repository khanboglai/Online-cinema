""" Routers for lk """
from datetime import datetime, timedelta
from fastapi import APIRouter, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, JSONResponse

from config import templates
from logs import logger
from exceptions.exceptions import UserIsExistError, UserEmailExistError
from schemas.user import EditUserRequest, ChangeUserSubscription
from services.user import UserDependency, edit_user, create_access_token, get_profile_by_user_id, get_age, \
    get_recently_watched, check_subscription, change_subscription as change_sub, get_subscription


""" Router initialize """
router = APIRouter(prefix="/lk", tags=["Personal Account"])


@router.get("/")
async def get_lk_html(user: UserDependency,
                      request: Request):
    """Personal account page"""
    if user is None:
        return RedirectResponse(url="/login")
    profile = await get_profile_by_user_id(user.id)
    number_of_recently_watched = 5
    recently_watched = await get_recently_watched(user.id, number_of_recently_watched)
    subscription = await get_subscription(user.id)
    is_sub_available = check_subscription(subscription)

    return templates.TemplateResponse(
        "lk.html",
        {
            "auth": user,
            "profile": profile,
            "age": get_age(profile.birth_date),
            "recently_watched": recently_watched,
            "subscription": subscription,
            "is_sub_available": is_sub_available,
            "request": request
        }
    )


@router.get("/edit")
async def get_edit_html(user: UserDependency,
                        request: Request):
    """Personal account edit page"""
    if user is None:
        return RedirectResponse(url="/login")
    profile = await get_profile_by_user_id(user.id)
    return templates.TemplateResponse(
        "edit_lk.html",
        {
            "request": request,
            "profile": profile,
            "auth": user,
        }
    )


@router.post("/edit")
async def edit(response: Response,
               user: UserDependency,
               form: EditUserRequest = Form()):
    """ Router for editing user info in all instances """
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


@router.post("/subscription")
async def change_subscription(subscription: ChangeUserSubscription = Form(...)):
    """ Router for change subscription plan """
    await change_sub(subscription)
