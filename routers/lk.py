from datetime import datetime, date
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from jinja2.runtime import TemplateReference
from sqlalchemy.sql.functions import session_user
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from routers.auth import get_current_user, DBDependency, bcrypt_context
from routers.pages import templates
from schemas.user import EditUserRequest, User

UserDependency = Annotated[User, Depends(get_current_user)]
router = APIRouter(prefix="/lk", tags=["Personal Account"])

@router.get("/")
async def get_lk_html(user: UserDependency,
                      request: Request):
    """Personal account page"""
    age: int | None = None
    if user.birth_date:
        age = (datetime.now().year - user.birth_date.year - ((datetime.now().month, datetime.now().day) < (user.birth_date.month, user.birth_date.day)))
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

def check_username_available(db: DBDependency, username: str) -> bool:
    result = db.query(User).filter(User.username == username).one_or_none()
    if result is None:
        return True
    return False

@router.post("/edit")
async def edit(db: DBDependency,
               user: UserDependency,
               response: Response,
               form: EditUserRequest = Form()):
    if form.username != user.username and check_username_available(db, user.username):
        user.username = form.username
    if form.new_password:
        user.hashed_password = bcrypt_context.hash(form.new_password)
    if form.birth_date:
        user.birth_date = form.birth_date
    if form.sex:
        user.sex = form.sex
    db.flush()
    db.commit()
    return RedirectResponse(url="/lk", status_code=status.HTTP_302_FOUND)

