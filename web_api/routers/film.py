from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from services.user import UserDependency
from services.film import get_film

router = APIRouter(
    prefix='/films',
    tags=['Filmpage']
)

templates = Jinja2Templates(directory="templates")
    
@router.get("/{film_id}")
async def get_film_html(user: UserDependency, request: Request, film_id: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        film = await get_film(film_id)
        return templates.TemplateResponse("film.html",
                                          {"request": request,
                                           "film": film,
                                           "cover": "/static/image.png",
                                           "video": "/static/video.mp4",
                                            })