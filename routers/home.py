import csv
import os
import base64
from collections import defaultdict
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from starlette.templating import Jinja2Templates
from routers.auth import get_current_user


router = APIRouter(
    prefix='',
    tags=['Homepage']
)

templates = Jinja2Templates(directory="templates")

UserDependency = Annotated[dict, Depends(get_current_user)]

async def get_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@router.get("/home")
async def get_home_html(user: UserDependency, request: Request):
    """Returns template for home page"""
    if user is None:
        return RedirectResponse(url="/login")
    else:
        # ОБРАЩЕНИЕ К МЛ МОДУЛЮ
        images_by_tag = defaultdict(list)
        with open('dataset.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                name = row['name']
                image_path = row['cover']
                tag = row['tag']
                if os.path.exists(image_path):
                    images_by_tag[tag].append({"cover": await get_image_base64(image_path),
                                               "name": name
                                               })
            # file.close()
        return templates.TemplateResponse("home.html", {"request": request, "films": images_by_tag})
