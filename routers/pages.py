"""Routers for pages displaying"""
from typing import Annotated
from fastapi import Request, APIRouter, Depends
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.templating import Jinja2Templates
from routers.auth import get_current_user

UserDependency = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="", tags=["Pages"])
templates = Jinja2Templates(directory="templates")

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