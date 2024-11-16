"""App"""
from typing import Annotated
from fastapi import FastAPI, status, Depends
from fastapi.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from repository.database import SessionLocal
from routers import auth, pages
from routers.auth import get_current_user

app = FastAPI()

app.include_router(auth.router)
app.include_router(pages.router)

app.mount('/static', StaticFiles(directory='static'), 'static')

UserDependency = Annotated[dict, Depends(get_current_user)]

@app.get("/", status_code=status.HTTP_200_OK)
async def user_auth(user: UserDependency):
    """Redirecting by cookies"""
    if user is None:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
