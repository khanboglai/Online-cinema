from datetime import datetime

from sqlalchemy import Column, String, Integer, Date, ForeignKey, ARRAY, Float, DateTime
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
    birth_date = Column(Date)
    sex = Column(String)
    email = Column(String, unique=True)

    # Связь 1 к 1 с таблицей Auth
    auth = relationship("Auth", back_populates="profile")

    # Связь 1 к 1 с таблицей Recommend
    recommend = relationship("Recommend", back_populates="profile")

    # Связь 1 ко многим с таблицей Interaction
    interaction = relationship("Interaction", back_populates="profile")

    # Связь 1 ко многим с таблицей Reply
    reply = relationship("Reply", back_populates="profile")

class Film(Base):
    __tablename__ = 'film'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    directors = Column(ARRAY(String))
    actors = Column(ARRAY(String))
    genres = Column(ARRAY(String))
    year = Column(Integer)
    countries = Column(ARRAY(String))
    studios = Column(String)
    tags = Column(ARRAY(String))
    rating_kp = Column(Float)
    age_rating = Column(Integer)

    # Связь 1 ко многим с таблицей Interaction
    interaction = relationship("Interaction", back_populates="film", cascade="all, delete-orphan")

    # Связь 1 ко многим с таблицей Reply
    reply = relationship("Reply", back_populates="film", cascade="all, delete-orphan")

    # Связь 1 ко многим с таблицей Recommend
    recommend = relationship("Recommend", back_populates="film", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = 'interaction'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    film_id = Column(Integer, ForeignKey('film.id', ondelete='CASCADE'))
    last_interaction = Column(DateTime)
    count_interaction = Column(Integer)
    watchtime = Column(Integer)

    profile = relationship("Profile", back_populates="interaction")

    film = relationship("Film", back_populates="interaction")

class Reply(Base):
    __tablename__ = 'reply'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    film_id = Column(Integer, ForeignKey('film.id', ondelete='CASCADE'))
    rating = Column(Float)
    text = Column(String)

    profile = relationship("Profile", back_populates="reply")

    film = relationship("Film", back_populates="reply")

class Recommend(Base):
    __tablename__ = 'recommend'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey('profile.id'))
    film_id = Column(Integer, ForeignKey('film.id', ondelete='CASCADE'))
    rank = Column(Integer)

    film = relationship("Film", back_populates="recommend")

    profile = relationship("Profile", back_populates="recommend")
