import os
import re
import logging
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.templating import Jinja2Templates
import boto3
from services.user import UserDependency
from services.film import get_film_by_id
from services.interaction import add_interaction, add_time_into_interaction


router = APIRouter(
    prefix='/films',
    tags=['Filmpage']
)

templates = Jinja2Templates(directory="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# тестово
# засунуть это в один файл
s3_client = boto3.client(
    's3',
    endpoint_url='http://storage:9000',
    aws_access_key_id='storage',
    aws_secret_access_key='qwerty2024',
)

BUCKET_NAME = 'storage-cinema'

# засунуть это в главный файл при запуске приложения создавать
try:
    s3_client.create_bucket(Bucket=BUCKET_NAME)
except Exception as e:
    logger.warning(f"S3: {e}")
    
@router.get("/{film_id}")
async def get_film_html(user: UserDependency, request: Request, film_id: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        await add_interaction(user.id, film_id)
        film = await get_film_by_id(film_id)
        return templates.TemplateResponse("film.html",
                                          {"request": request,
                                           "film": film,
                                           "cover": "/static/image.png"})

    
@router.get("/video/{film_id}")
async def get_video(request: Request, film_id: int):
    """For streaming films"""
    # обращение к бд, чтобы достать путь к фильму по его айдишнику, пока хардкод

    film = await get_film_by_id(film_id)

    # Получаем метаданные о видеофайле
    head_response = s3_client.head_object(Bucket=BUCKET_NAME, Key=f"{film_id}/{film.name}.mp4")
    file_size = head_response['ContentLength']
    range_header = request.headers.get('Range', None)

    if range_header is None:
        # Если диапазон не указан, отправляем весь файл
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{film_id}/{film.name}.mp4")
        video_path = response["Body"]
        return StreamingResponse(video_path, media_type="video/mp4")

    # Обработка диапазона
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        raise HTTPException(status_code=416)

    start, end = range_match.groups()
    start = int(start)
    end = int(end) if end else file_size - 1

    if start > end or start < 0 or end >= file_size:
        raise HTTPException(status_code=416)

    length = end - start + 1
    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(length),
        'Content-Type': 'video/mp4',
    }

    # Запрашиваем диапазон данных из S3
    range_header = f"bytes={start}-{end}"
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{film_id}/{film.name}.mp4", Range=range_header)
    video_stream = response["Body"]

    return StreamingResponse(video_stream, headers=headers, media_type="video/mp4", status_code=206)

    # def video_stream():
    #     with open(video_path, "rb") as video_file:
    #         while chunk := video_file.read(1024 * 1024):  # Читаем по 1 МБ за раз
    #             yield chunk

    # return StreamingResponse(video_stream(), media_type="video/mp4")


@router.post('/watchtime/{film_id}')
async def record_watchtime(user: UserDependency, film_id: int, time_watched: dict):
    time = time_watched.get("timeWatched")
    await add_time_into_interaction(user.id, film_id, time)
    