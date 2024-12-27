""" App """
import logging
import os
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from routers import auth, lk, home, upload_film, film, search, manage
from services.user import UserDependency
from config import s3_client, BUCKET_NAME


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """ Function for app starting and setting """
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        logger.info("S3 Bucket created successfully")
    except Exception as e:
        logger.warning(f"S3: {e}")

    logger.info("App started")
    
    yield

    logger.info("App stopped")


app = FastAPI(lifespan=lifespan)


""" Routers including """
app.include_router(auth.router)
app.include_router(lk.router)
app.include_router(home.router)
app.include_router(upload_film.router)
app.include_router(film.router)
app.include_router(search.router)
app.include_router(manage.router)


""" Static files initialization """
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), 'static')


@app.get("/", status_code=status.HTTP_200_OK)
async def user_auth(user: UserDependency):
    """ Redirecting by cookies """
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """ Handler for undefined path """
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
