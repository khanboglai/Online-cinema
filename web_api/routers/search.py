from collections import defaultdict
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from boto3.exceptions import Boto3Error

from services.user import UserDependency
from services.search import get_search_results
from services.film import get_film_by_id
from config import s3_client, BUCKET_NAME
from logs import logger


router = APIRouter(
    prefix='/search',
    tags=['Search']
)

templates = Jinja2Templates(directory="templates")


@router.get("/{search_query}/page={page}")
async def get_search_results_html(user: UserDependency, request: Request, search_query: str, page: int):
    if user is None:
        return RedirectResponse(url="/login")

    images_by_tag = defaultdict(list)
    response = await get_search_results(search_query, page)

    for hit in response:
        film = await get_film_by_id(int(hit["_id"]))
        cover_key = f"{film.id}/image.png"

        try:
            cover_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': cover_key},
                ExpiresIn=3600
            )
            cover_url = cover_url.replace("storage", "localhost", 1)
            logger.info("Cover response success")
        except Boto3Error as e:
            logger.exception(e)
            cover_url = "/static/image.png"

        images_by_tag[f'Фильмы по запросу: "{search_query}"'].append({"cover": cover_url,
                                                                      "name": film.name,
                                                                      "id": film.id},)
    if len(images_by_tag) == 0:
        return templates.TemplateResponse("search.html", {"request": request, "films": None, "user": user})
    else:
        return templates.TemplateResponse("search.html", {"request": request, "films": images_by_tag, "user": user})
        

@router.get("/suggestions/{search_query}")
async def get_suggestions_query(request: Request, search_query: str):
    response = await get_search_results(search_query, 1)
    return {"suggestions": [{"id": hit["_id"], "title": hit["_source"]["title"]} for hit in response]}
            
