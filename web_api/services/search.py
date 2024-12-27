""" Functions for working with elasticsearch """
import logging
from elasticsearch import Elasticsearch


""" Logger initialize """
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


""" Elasticsearch initialize """
es = Elasticsearch(f"http://elasticsearch:9200")


async def get_search_results(search_query: str, page: int):
    """ Getter of search results for films by pages """
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
    """ Getter of search results for users by pages """
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
    """ Function for adding film to es  """
    document = {'title': title}
    response = es.index(index='films', id=id, document=document)
    logger.info(f"film {title} added to elastic with id {id}")


async def update_document(title: str, id: int):
    """ Function for updating film in es """
    document = {
        "doc": {
            "title": title
        }
    }
    response = es.update(index='films', id=id, body=document)
    logger.info(f"film {title} updated to elastic with id {id}")


async def add_user_to_es(user_id: int, login: str):
    """ Function for adding user to es """
    document = {'login': login}
    response = es.index(index='users', id=user_id, document=document)
    logger.info(f"user {login} added to elastic with id {user_id}")


async def delete_document(id: int):
    """ Function for deleting film from es """
    response = es.delete(index='films', id=id)
    logger.info(f"film with id {id} deleted from elastic")


async def delete_user_from_es(user_id: int):
    """ Function for deleting user from es """
    response = es.delete(index='users', id=user_id)
    logger.info(f"user with id {user_id} deleted from elastic")

async def update_user_in_es(login: str, user_id: int):
    """ Function for updating user in es """
    document = {
        "doc": {
            "login": login
        }
    }
    response = es.update(index='users', id=user_id, body=document)
    logger.info(f"user {login} updated in elastic")
