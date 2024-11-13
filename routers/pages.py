from fastapi import Request

from fastapi import APIRouter
from starlette.templating import Jinja2Templates

from routers.auth import router

router = APIRouter(prefix="", tags=["Pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
async def get_register_html(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
