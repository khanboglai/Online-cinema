import os
from elasticsearch import Elasticsearch

ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_PORT = os.getenv("ELASTIC_PORT")

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