from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, Float, Time
from sqlalchemy.orm import relationship

from repository.database import Base

class Auth(Base):
    __tablename__ = 'auth'
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)

    # Связь 1 к 1 с таблицей Profile
    profile = relationship("Profile", back_populates="auth", uselist=False)

class Profile(Base):
    """Definition of table Profile"""
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    auth_id = Column(Integer, ForeignKey('auth.id'))
    name = Column(String)
    surname = Column(String)
    birth_date = Column(DateTime)
    sex = Column(String)
    ebals = Column(Integer)
    email = Column(String, unique=True)

    # Связь 1 к 1 с таблицей Auth
    auth = relationship("Auth", back_populates="profile")

    # Связь 1 ко многим с таблицей Interaction
    interaction = relationship("Interaction", back_populates="profile")

class Film(Base):
    __tablename__ = 'film'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    file_path = Column(String)
    directors = Column(ARRAY(String))
    actors = Column(ARRAY(String))
    genres = Column(ARRAY(String))
    year = Column(Integer)
    country = Column(String)
    studios = Column(String)
    tags = Column(ARRAY(String))
    rating_kp = Column(Float)

    # Связь 1 ко многим с таблицей Interaction
    interaction = relationship("Interaction", back_populates="film")

class Interaction(Base):
    __tablename__ = 'interaction'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    film_id = Column(Integer, ForeignKey('film.id'))
    last_interaction = Column(Time)
    count_interaction = Column(Integer)

    profile = relationship("Profile", back_populates="interaction")

    film = relationship("Film", back_populates="interaction")
