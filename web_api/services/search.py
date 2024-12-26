import os
import logging
from elasticsearch import Elasticsearch

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_PORT = os.getenv("ELASTIC_PORT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

es = Elasticsearch(f"http://elasticsearch:9200")

async def get_search_results(search_query: str, page: int):
    response = es.search(
        index="films",
        body={
            "from": (page - 1) * 9,
            "size": 9,
            "query": {
                "match_phrase_prefix": {
                    "title": search_query
                }
            },
        }
    )
    return response["hits"]["hits"]

async def get_user_search_results(search_query: str, page: int):
    response = es.search(
        index="users",
        body={
            "from": (page - 1) * 9,
            "size": 9,
            "query": {
                "match_phrase_prefix": {
                    "login": search_query
                }
            },
        }
    )
    return response["hits"]["hits"]

async def add_document(title: str, id: int):
    document = {'title': title}
    response = es.index(index='films', id=id, document=document)

async def add_user_to_es(user_id: int, login: str):
    document = {'login': login}
    response = es.index(index='users', id=user_id, document=document)

async def delete_document(id: int):
    response = es.delete(index='films', id=id)

async def delete_user_from_es(user_id: int):
    response = es.delete(index='users', id=user_id)
