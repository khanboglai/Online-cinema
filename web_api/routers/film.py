import os
import re

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError

from config import s3_client, BUCKET_NAME
from config import templates
from services.user import UserDependency
from services.film import get_film_by_id, add_comment_to_db, get_all_comments, delete_film
from services.interaction import add_interaction, add_time_into_interaction
from schemas.comment import Comment, CommentRequest
from logs import logger


router = APIRouter(prefix='/films', tags=['Filmpage'])

    
@router.get("/{film_id}")
async def get_film_html(user: UserDependency, request: Request, film_id: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        await add_interaction(user.id, film_id)
        film = await get_film_by_id(film_id)
        if film.rating_kp is not None:
            film.rating_kp = round(film.rating_kp, 1)   
        
        logger.info(f"Film response successed for {user.login}")
        admin = False
        if user.role == 'ROLE_ADMIN':
            admin = True
        return templates.TemplateResponse("film.html",
                                          {"request": request,
                                           "film": film,
                                           "admin": admin,
                                        #    "cover": cover_url,
                                           })

    
@router.get("/video/{film_id}")
async def get_video(request: Request, film_id: int):
    """For streaming films"""
    # обращение к бд, чтобы достать путь к фильму по его айдишнику, пока хардкод

    film = await get_film_by_id(film_id)

    # Получаем метаданные о видеофайле
    head_response = s3_client.head_object(Bucket=BUCKET_NAME, Key=f"{film_id}/video.mp4")
    file_size = head_response['ContentLength']
    range_header = request.headers.get('Range', None)

    if range_header is None:
        # Если диапазон не указан, отправляем весь файл
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{film_id}/video.mp4")
        video_path = response["Body"]
        logger.warning("Range header undefined")
        return StreamingResponse(video_path, media_type="video/mp4")

    # Обработка диапазона
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        logger.error("Undefined range")
        raise HTTPException(status_code=416)

    start, end = range_match.groups()
    start = int(start)
    end = int(end) if end else file_size - 1

    if start > end or start < 0 or end >= file_size:
        logger.error("Range error definition")
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
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=f"{film_id}/video.mp4", Range=range_header)
    video_stream = response["Body"]

    logger.info("Video stream response completed")
    return StreamingResponse(video_stream, headers=headers, media_type="video/mp4", status_code=206)


@router.post('/watchtime/{film_id}')
async def record_watchtime(user: UserDependency, film_id: int, time_watched: dict):
    time = time_watched.get("timeWatched")
    await add_time_into_interaction(user.id, film_id, time)


@router.post('/{film_id}/comments')
async def add_comment(user: UserDependency, film_id: int, request: Request):
    data = await request.json()
    comment = Comment(**data)
    comment_to_db = CommentRequest(user_id=user.id, rating=comment.rating, text=comment.text, film_id=film_id)
    await add_comment_to_db(comment_to_db)


@router.get('/{film_id}/comments')
async def get_comments(request: Request, film_id: int):
    comments = await get_all_comments(film_id)
    return [{"name": comment.name, "surname": comment.surname, "rating": comment.rating, "text": comment.text} for comment in comments]

@router.post('/delete/{film_id}')
async def delete_film_request(request: Request, film_id: int):
    try:
        await delete_film(film_id)
    except SQLAlchemyError as e:
        logger.error(f"Delete from pg error: {e}")
        return JSONResponse(status_code=500, content={"error": "Something occured with db, try again!"})
    