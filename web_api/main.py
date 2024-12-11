"""App"""
from typing import Annotated
from fastapi import FastAPI, status, Depends
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from repository.database import SessionLocal
from routers import auth, lk, home, upload_film, film, search
from services.user import UserDependency

app = FastAPI()

app.include_router(auth.router)
app.include_router(lk.router)
app.include_router(home.router)
app.include_router(upload_film.router)
app.include_router(film.router)
app.include_router(search.router)

app.mount('/static', StaticFiles(directory='static'), 'static')

@app.get("/", status_code=status.HTTP_200_OK)
async def user_auth(user: UserDependency):
    """Redirecting by cookies"""
    if user is None:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
