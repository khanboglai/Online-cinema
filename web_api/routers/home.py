import pandas as pd
from collections import defaultdict
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from starlette.templating import Jinja2Templates
from services.user import UserDependency
from services.film import get_film_title

import httpx

router = APIRouter(
    prefix='',
    tags=['Homepage']
)

templates = Jinja2Templates(directory="templates")

@router.get("/home")
async def get_home_html(user: UserDependency, request: Request):
    """Returns template for home page"""
    if user is None:
        return RedirectResponse(url="/login")
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ml:8080/recommend/{user.id}")  # Обращаемся ко второму API
        images_by_tag = defaultdict(list)
        for film in response.json()["recommendations"]:
            name = await get_film_title(film)
            images_by_tag["Recommended"].append({"cover": "/static/image.png",
                                                 "name": name,
                                                 "id": film},)
        return templates.TemplateResponse("home.html", {"request": request, "films": images_by_tag})

