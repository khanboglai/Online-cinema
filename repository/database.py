"""Session maker with database"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import get_db_url
# ЕСЛИ НАДО БУДЕТ ЗАПУСТИТЬ, НАДО ПОМЕНЯТЬ ПОРТ НА 5432 ЛИБО КОГДА ПОДНИМАЕШЬ ПОСТГРЮ ПОСТАВЬ ЛОКАЛЬНЫЙ ПОРТ 5442
# ПРОСТО Я ДУРЕНЬ НЕ СМОГ ЗАПУСТИТЬ ДОКЕР НА 5432 ПОРТУ
URL_DATABASE = get_db_url()
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# """Session maker with database"""
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# from config import get_db_url

# URL_DATABASE = get_db_url()

# engine = create_async_engine(URL_DATABASE)

# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
