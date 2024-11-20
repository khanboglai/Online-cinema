from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.requests import Request

from routers.auth import get_current_user
from routers.pages import templates

UserDependency = Annotated[dict, Depends(get_current_user)]
router = APIRouter(prefix="/lk", tags=["Personal Account"])

@router.get("/")
async def get_lk_html(user: UserDependency, request: Request):
    return templates.TemplateResponse("lk.html", {"user": user, "request": request})

@router.get("/edit")
async def get_edit_html(user: UserDependency, request: Request):
    return "edit page"
