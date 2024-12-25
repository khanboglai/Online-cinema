from collections import defaultdict
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, StreamingResponse, FileResponse
from starlette.templating import Jinja2Templates
from boto3.exceptions import Boto3Error

from services.user import UserDependency
from services.film import get_newest_films, get_recommend_films, get_film_by_id
from config import s3_client, BUCKET_NAME


import httpx

router = APIRouter(
    prefix='',
    tags=['Homepage']
)

templates = Jinja2Templates(directory="templates")

@router.get("/home")
async def get_home_html(user: UserDependency, request: Request):
    """ Returns template for home page """
    if user is None:
        return RedirectResponse(url="/login")
    else:
        images_by_tag = defaultdict(list)
        film_ids = await get_recommend_films(user.id)
        if film_ids is not None:
            for film_id in film_ids:
                film = await get_film_by_id(film_id)
                # cover_key = f"{film.id}/image.png"
                # try:
                #     cover_url = s3_client.generate_presigned_url(
                #         'get_object',
                #         Params={'Bucket': BUCKET_NAME, 'Key': cover_key},
                #         ExpiresIn=3600
                #     )
                #     cover_url = cover_url.replace("storage", "0.0.0.0", 1)
                # except Boto3Error:
                #     cover_url = "/static/image.png"
                images_by_tag["Recommended"].append({
                                                    # "cover": cover_url,
                                                    "name": film.name,
                                                    "id": film.id,
                                                    })
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(f"http://ml:8080/recommend/{user.id}")  # Обращаемся ко второму API
        # images_by_tag = defaultdict(list)
        # for film in response.json()["recommendations"]:
        #     name = await get_film_title(film)
        #     images_by_tag["Recommended"].append({"cover": "/static/image.png",
        #                                          "name": name,
        #                                          "id": film},)

        # Выдача новинок
        films = await get_newest_films()
        for film in films:
            # cover_key = f"{film.id}/image.png"
            # try:
            #     cover_url = s3_client.generate_presigned_url(
            #         'get_object',
            #         Params={'Bucket': BUCKET_NAME, 'Key': cover_key},
            #         ExpiresIn=3600
            #     )
            #     cover_url = cover_url.replace("storage", "0.0.0.0", 1)
            # except Boto3Error:
            #     cover_url = "/static/image.png"
            images_by_tag["New"].append({
                                        #  "cover": cover_url,
                                         "name": film.name,
                                         "id": film.id,
                                         })
        # images_by_tag = None
        if user.role == 'ROLE_ADMIN':
            return templates.TemplateResponse("home_admin.html", {"request": request,
                                                        "films": images_by_tag})
        else:
            return templates.TemplateResponse("home.html", {"request": request,
                                                        "films": images_by_tag})
        
@router.get("/image/{film_id}")
async def get_image_by_id(request: Request, film_id: int):
    cover_key = f"{film_id}/image.png"
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=cover_key)
        return StreamingResponse(response['Body'], media_type="image/png")
    except Boto3Error:
        cover_url = "/static/image.png"
        return FileResponse(cover_url, media_type="image/png")

    

