from collections import defaultdict
from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates
from services.user import UserDependency
from services.search import get_search_results

router = APIRouter(
    prefix='/search',
    tags=['Search']
)

templates = Jinja2Templates(directory="templates")

@router.get("/{search_query}/page={page}")
async def get_search_results_html(user: UserDependency, request: Request, search_query: str, page: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        images_by_tag = defaultdict(list)
        response = await get_search_results(search_query, page)
        for hit in response:
            images_by_tag[f'Фильмы по запросу: "{search_query}"'].append({"cover": "/static/image.png",
                                                                          "name": hit["_source"]["title"],
                                                                          "id": hit["_id"]},)
        if len(images_by_tag) == 0:
            return templates.TemplateResponse("search.html", {"request": request, "films": None})
        else:
            return templates.TemplateResponse("search.html", {"request": request, "films": images_by_tag})
            
