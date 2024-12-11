import os
from typing import Annotated
from collections import defaultdict
from fastapi import APIRouter, Request, Depends
from starlette.templating import Jinja2Templates
from elasticsearch import Elasticsearch
from routers.auth import get_current_user_id


router = APIRouter(
    prefix='/search',
    tags=['Search']
)

templates = Jinja2Templates(directory="templates")

UserDependency = Annotated[dict, Depends(get_current_user_id)]

ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

es = Elasticsearch("http://elasticsearch:9200")

@router.get("/{search_query}/page={page}")
async def get_search_results_html(user: UserDependency, request: Request, search_query: str, page: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        # перенести в services
        images_by_tag = defaultdict(list)
        response = es.search(
            index="films",
            body={
                "from": (page - 1) * 10,
                "size": 10,
                "query": {
                    "match_phrase_prefix": {
                        "title": search_query
                    }
                },
            }
        )
        for hit in response["hits"]["hits"]:
            images_by_tag[f'Фильмы по запросу: "{search_query}"'].append({"cover": "/static/image.png",
                                                                          "name": hit["_source"]["title"],
                                                                          "id": hit["_id"]},)
        if len(images_by_tag) == 0:
            return templates.TemplateResponse("search.html", {"request": request, "films": None})
        else:
            return templates.TemplateResponse("search.html", {"request": request, "films": images_by_tag})
            
