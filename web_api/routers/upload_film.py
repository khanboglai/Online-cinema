from urllib import request

from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Form
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from config import templates
from services.film import save_film
from services.user import UserDependency

router = APIRouter(prefix="/upload")

@router.get("/")
async def upload_film_html(request: Request, user: UserDependency):
    '''
    GET (/upload) endpoint
    :param request:
    :return:
    '''
    if user is None:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("upload_film.html", {"request": request})

@router.post("/")
async def upload_film(
        response: Response,
        film_name: str = Form(...),
        age_rating: int = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        country: str = Form(...),
        description: str = Form(...),
        actor: str = Form(...),
        genre: str = Form(...),
        studios: str = Form(...),
        tags: str = Form(...),
        film_file: UploadFile = File(...),
        film_cover: UploadFile = File(...)
):
    '''
    POST (/upload) endpoint
    :param film_name:
    :param film_file:
    :param country:
    :param year:
    :param director:
    :param age_rating:
    :param response:
    :return:
    '''
    if film_file.content_type != 'video/mp4':
        raise HTTPException(status_code=400, detail="Файл должен быть в формате MP4")
    
    if film_cover.content_type != 'image/png':
        raise HTTPException(status_code=400, detail="Файл должен быть в формате PNG")
    

    try:
        await save_film(film_name, age_rating, director, year, country, description, actor, genre, studios, tags, film_file, film_cover)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail=repr(e))

    return Response(status_code=status.HTTP_200_OK)
