"""
Service layer for films.
"""

import os

import pandas as pd

import aiofiles
from fastapi import UploadFile, Form

# from repository.film_dao import FilmDao

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# dao = FilmDao()

# async def save_film(
#         film_name: str,
#         age_rating: str,
#         director: str,
#         year: int,
#         country: str,
#         file: UploadFile):
#     '''
#     Service for saving films into storage
#     :param file:
#     :param upload_form:
#     :return:
#     '''

#     print("Save film")

#     film = await dao.add(
#         name=film_name,
#         age_rating=age_rating,
#         director=director,
#         year=year,
#         country=country,
#     )

#     print("film added: " + film_name)

#     file_location = os.path.join(UPLOAD_FOLDER, str(film.id) + "_" + film.name)

#     async with aiofiles.open(file_location, "wb") as out_file:
#         content = await file.read()
#         await out_file.write(content)

# пока что из csv
async def get_film(film_id: int):
    df = pd.read_csv('static/data/items.csv')
    df["date"] = df["date"].fillna(0).astype(int)
    df["rating_kp"] = df["rating_kp"].fillna(-1)
    return df[(df["item_id"] == film_id)]

async def get_film_title(film_id: int):
    df = pd.read_csv('static/data/items.csv')
    df["date"] = df["date"].fillna(0).astype(int)
    df["rating_kp"] = df["rating_kp"].fillna(-1)
    return df[(df["item_id"] == film_id)]["title"].to_string(index=False)
