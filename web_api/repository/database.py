"""Session maker with database"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase
from config import get_db_url


URL_DATABASE = get_db_url()
engine = create_async_engine(URL_DATABASE)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
