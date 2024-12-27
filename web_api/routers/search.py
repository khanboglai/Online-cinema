""" Routers for search actions """
from collections import defaultdict
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from services.user import UserDependency
from config import templates
from services.search import get_search_results
from services.film import get_film_by_id


""" Router initialize """
router = APIRouter(
    prefix='/search',
    tags=['Search']
)


@router.get("/{search_query}/page={page}")
async def get_search_results_html(user: UserDependency, request: Request, search_query: str, page: int):
    """ Get page with film search results """
    if user is None:
        return RedirectResponse(url="/login")

    images_by_tag = defaultdict(list)
    response = await get_search_results(search_query, page)

    for hit in response:
        film = await get_film_by_id(int(hit["_id"]))
        images_by_tag[f'Фильмы по запросу: "{search_query}"'].append({
                                                                    "name": film.name,
                                                                    "id": film.id
                                                                    },)
    if len(images_by_tag) == 0:
        return templates.TemplateResponse("search.html", {"request": request, "films": None, "user": user})
    else:
        return templates.TemplateResponse("search.html", {"request": request, "films": images_by_tag, "user": user})
        

@router.get("/suggestions/{search_query}")
async def get_suggestions_query(request: Request, search_query: str):
    """ Get film searcgh suggustions """
    response = await get_search_results(search_query, 1)
    return {"suggestions": [{"id": hit["_id"], "title": hit["_source"]["title"]} for hit in response]}
            