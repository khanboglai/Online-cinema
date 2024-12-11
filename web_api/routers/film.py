import pandas as pd
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from starlette.templating import Jinja2Templates
from routers.auth import get_current_user_id

router = APIRouter(
    prefix='/films',
    tags=['Filmpage']
)

templates = Jinja2Templates(directory="templates")

UserDependency = Annotated[dict, Depends(get_current_user_id)]
    
@router.get("/{film_id}")
async def get_film_html(user: UserDependency, request: Request, film_id: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        df = pd.read_csv('static/data/items.csv')
        df["date"] = df["date"].fillna(0).astype(int)
        df["rating_kp"] = df["rating_kp"].fillna(-1)
        return templates.TemplateResponse("film.html",
                                          {"request": request,
                                           "film": df[(df["item_id"] == film_id)],
                                           "cover": "/static/image.png",
                                           "video": "/static/video.mp4",
                                            })