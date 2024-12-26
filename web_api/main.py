"""App"""
import logging
import os
import asyncio
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from routers import auth, lk, home, upload_film, film, search, manage
from services.user import UserDependency
from config import s3_client, BUCKET_NAME
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(auth.router)
app.include_router(lk.router)
app.include_router(home.router)
app.include_router(upload_film.router)
app.include_router(film.router)
app.include_router(search.router)
app.include_router(manage.router)

app.mount('/static', StaticFiles(directory='static'), 'static')


@asynccontextmanager
async def lifespan(_: FastAPI):
    """ Функция для запуска приложения и настройки системы """
    try:
        s3_client.create_bucket(Bucket=BUCKET_NAME)
        logger.info("S3 Bucket created successfully")
    except Exception as e:
        logger.warning(f"S3: {e}")

    logger.info("App started")
    
    yield

    logger.info("App stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(lk.router)
app.include_router(home.router)
app.include_router(upload_film.router)
app.include_router(film.router)
app.include_router(search.router)
app.include_router(manage.router)

static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), 'static')



@app.get("/", status_code=status.HTTP_200_OK)
async def user_auth(user: UserDependency):
    """ Redirecting by cookies """
    if user is None:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)

# обработчик для несуществующего маршрута
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
