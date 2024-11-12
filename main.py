from fastapi import FastAPI, status, Depends, HTTPException
from models import models
from repository.database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from routers import auth
from routers.auth import get_current_user
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.include_router(auth.router)
# Директория для шаблонов
templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_cureent_user)]

# сюда шаблон без дизайна можно пока, просто чтобы там какой нибудь привет мир висел
@app.get("/", status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification Failed')
    return {"User": user}