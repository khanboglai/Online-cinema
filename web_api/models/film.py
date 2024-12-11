"""
Film ORM model.
"""

from sqlalchemy import Column, Integer, String

from repository.database import Base

class Film(Base):
    __tablename__ = 'Film'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age_rating = Column(String)
    director = Column(String)
    year = Column(Integer)
    country = Column(String)
