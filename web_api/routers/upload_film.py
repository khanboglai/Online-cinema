from urllib import request

from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Form
from fastapi.params import Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from config import templates
from services.film import save_film

router = APIRouter(prefix="/upload")

@router.get("/")
async def upload_film_html(request: Request):
    '''
    GET (/upload) endpoint
    :param request:
    :return:
    '''

    return templates.TemplateResponse("upload_film.html", {"request": request})

@router.post("/")
async def upload_film(
        response: Response,
        film_name: str = Form(...),
        age_rating: str = Form(...),
        director: str = Form(...),
        year: int = Form(...),
        country: str = Form(...),
        film_file: UploadFile = File(...)
):
    '''
    POST (/upload) endpoint
    :param file:
    :param upload_form:
    :param response:
    :return:
    '''

    try:
        await save_film(film_name, age_rating, director, year, country, film_file)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                      detail="Can't save film")

    return Response(status_code=status.HTTP_200_OK)
