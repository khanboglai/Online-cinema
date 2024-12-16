import os
import re
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, StreamingResponse
from starlette.templating import Jinja2Templates
from services.user import UserDependency
from services.film import get_film_by_id

router = APIRouter(
    prefix='/films',
    tags=['Filmpage']
)

templates = Jinja2Templates(directory="templates")
    
@router.get("/{film_id}")
async def get_film_html(user: UserDependency, request: Request, film_id: int):
    if user is None:
        return RedirectResponse(url="/login")
    else:
        film = await get_film_by_id(film_id)
        return templates.TemplateResponse("film.html",
                                          {"request": request,
                                           "film": film,
                                           "cover": "/static/image.png",
                                        #    "video": "/static/video.mp4",
                                            })
    
@router.get("/video/{film_id}")
async def get_video(request: Request, film_id: int):
    # обращение к бд, чтобы достать путь к фильму по его айдишнику, пока хардкод
    video_path = "static/video.mp4"
    file_size = os.path.getsize(video_path)
    range_header = request.headers.get('Range', None)

    if range_header is None:
        # Если диапазон не указан, отправляем весь файл
        return StreamingResponse(open(video_path, "rb"), media_type="video/mp4")
    
    # Обработка диапазона
    range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
    if not range_match:
        return Response(status_code=416)
    
    start, end = range_match.groups()
    start = int(start)
    end = int(end) if end else file_size - 1

    if start > end or start < 0 or end >= file_size:
        return Response(status_code=416)

    length = end - start + 1
    headers = {
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Accept-Ranges': 'bytes',
        'Content-Length': str(length),
        'Content-Type': 'video/mp4',
    }

    async def video_stream():
        with open(video_path, "rb") as video_file:
            video_file.seek(start)
            while True:
                chunk = video_file.read(1024 * 1024)  # Читаем по 1 МБ за раз
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(video_stream(), headers=headers, media_type="video/mp4", status_code=206)

    # def video_stream():
    #     with open(video_path, "rb") as video_file:
    #         while chunk := video_file.read(1024 * 1024):  # Читаем по 1 МБ за раз
    #             yield chunk

    # return StreamingResponse(video_stream(), media_type="video/mp4")
    