import os

import aiofiles
from fastapi import UploadFile, Form

UPLOAD_FOLDER = "/app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def save_film(
        film_name: str,
        age_rating: str,
        director: str,
        year: int,
        country: str,
        file: UploadFile):
    '''
    Service for saving films into storage
    :param file:
    :param upload_form:
    :return:
    '''
    print("DEBUG: saving film")

    file_location = os.path.join(UPLOAD_FOLDER, film_name)

    async with aiofiles.open(file_location, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
