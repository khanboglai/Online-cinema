from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Form
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from config import templates
from schemas.user import EditUserRequest
from services.user import get_age, UserDependency, edit_user, create_access_token

router = APIRouter(prefix="/lk", tags=["Personal Account"])

@router.get("/")
async def get_lk_html(user: UserDependency,
                      request: Request):
    """Personal account page"""
    age: int | None = None
    if user.birth_date:
        age = get_age(user.birth_date)
    return templates.TemplateResponse(
        "lk.html",
        {
            "username": user.username,
            "request": request,
            "age": age
        }
    )

@router.get("/edit")
async def get_edit_html(user: UserDependency,
                        request: Request):
    """Personal account edit page"""
    return templates.TemplateResponse(
        "edit_lk.html",
        {
            "request": request,
            "username": user.username,
        }
    )

@router.post("/edit")
async def edit(response: Response,
               user: UserDependency,
               form: EditUserRequest = Form()):
    new_user = await edit_user(user, form)
    access_token = create_access_token(new_user.username,
                                       new_user.id)
    response.set_cookie(key="access_token", value=access_token, max_age=datetime.utcnow() + timedelta(hours=1))
    return RedirectResponse(url="/lk", status_code=status.HTTP_302_FOUND)
