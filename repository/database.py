from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ЕСЛИ НАДО БУДЕТ ЗАПУСТИТЬ, НАДО ПОМЕНЯТЬ ПОРТ НА 5432 ЛИБО КОГДА ПОДНИМАЕШЬ ПОСТГРЮ ПОСТАВЬ ЛОКАЛЬНЫЙ ПОРТ 5442
# ПРОСТО Я ДУРЕНЬ НЕ СМОГ ЗАПУСТИТЬ ДОКЕР НА 5432 ПОРТУ
URL_DATABASE = 'postgresql://postgres:qwerty@localhost:5442/cinema'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()