from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from config import templates

from services.user import UserDependency

router = APIRouter(
    prefix='/manage',
    tags=['Admin panel']
)

@router.get("/")
async def get_manage_html(request: Request, user: UserDependency):
     if user is None or user.role != 'ROLE_ADMIN':
        return RedirectResponse(url="/login")
     return templates.TemplateResponse("manage.html", {"request": request})