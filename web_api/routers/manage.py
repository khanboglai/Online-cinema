""" Routers for users managment by admin """
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from config import templates
from services.user import delete_user, UserDependency
from services.search import get_user_search_results


""" Router initialize """
router = APIRouter(
    prefix='/manage',
    tags=['Admin panel']
)


@router.get("/")
async def get_manage_html(request: Request, user: UserDependency):
     """ Get users manage page"""
     if user is None or user.role != 'ROLE_ADMIN':
        return RedirectResponse(url="/login")
     return templates.TemplateResponse("manage.html", {"request": request})


@router.post("/delete/{user_id}")
async def delete_user_request(request: Request, user_id: int):
    """ Function for deleting user and all information about him on site """
    await delete_user(user_id)

@router.get("/suggest/{query}")
async def get_user_suggests(request: Request, query: str):
    """ Function for getting user suggests to delete """
    response = await get_user_search_results(query, 1)
    return {"suggestions": [{"id": hit["_id"], "login": hit["_source"]["login"]} for hit in response]}
