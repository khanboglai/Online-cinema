"""Session maker with database"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import get_db_url

URL_DATABASE = get_db_url()
engine = create_async_engine(URL_DATABASE)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()
