from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from config import templates
from schemas.user import EditUserRequest
from services.user import get_age, UserDependency, edit_user, create_access_token, get_birth_date_by_user_id, get_name_by_user_id, get_surname_by_user_id, get_email_by_user_id

router = APIRouter(prefix="/lk", tags=["Personal Account"])

@router.get("/")
async def get_lk_html(user: UserDependency,
                      request: Request):
    """Personal account page"""
    birth_date: datetime | None = await get_birth_date_by_user_id(user)
    age: int | None = None
    if birth_date:
        age = get_age(birth_date)
    name: str | None = await get_name_by_user_id(user)
    surname: str | None = await get_surname_by_user_id(user)
    return templates.TemplateResponse(
        "lk.html",
        {
            "name": name,
            "surname": surname,
            "request": request,
            "age": age
        }
    )

@router.get("/edit")
async def get_edit_html(user: UserDependency,
                        request: Request):
    """Personal account edit page"""
    name: str | None = await get_name_by_user_id(user)
    surname: str | None = await get_surname_by_user_id(user)
    birth_date: datetime | None = await get_birth_date_by_user_id(user)
    email: str | None = await get_email_by_user_id(user)
    return templates.TemplateResponse(
        "edit_lk.html",
        {
            "request": request,
            "name": name,
            "surname": surname,
            "birth_date": birth_date,
            "email": email,
        }
    )

@router.post("/edit")
async def edit(response: Response,
               user: UserDependency,
               form: EditUserRequest = Form()):
    new_user = await edit_user(user, form)
    # access_token = create_access_token(new_user.username,
    #                                    new_user.id)
    response = RedirectResponse(url="/lk", status_code=status.HTTP_302_FOUND)
    # response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return response
