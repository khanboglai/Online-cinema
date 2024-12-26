from collections import defaultdict
from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, StreamingResponse, FileResponse
from starlette.templating import Jinja2Templates
from boto3.exceptions import Boto3Error

from logs import logger
from config import templates
from services.user import UserDependency
from services.film import get_newest_films, get_recommend_films, get_film_by_id
from config import s3_client, BUCKET_NAME


router = APIRouter(
    prefix='',
    tags=['Homepage']
)

@router.get("/home")
async def get_home_html(user: UserDependency, request: Request):
    """ Returns template for home page """
    if user is None:
        return RedirectResponse(url="/login")
    else:
        images_by_tag = defaultdict(list)
        recs = await get_recommend_films(user.id)
        # здесь надо будет проверить этот список и в случае его пустоты отдать рекомендации профиля с id=0 
        if recs is not None:
            for rec in recs:
                film = await get_film_by_id(rec.film_id)
                images_by_tag["Recommended"].append({
                                                    # "cover": cover_url,
                                                    "name": film.name,
                                                    "id": film.id,
                                                    })

        # Выдача новинок
        films = await get_newest_films()
        for film in films:
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
    except Boto3Error as e:
        logger.error(f"Error Boto3: {e}")
        cover_url = "/static/image.png"
        return FileResponse(cover_url, media_type="image/png")
