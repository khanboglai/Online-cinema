from sqlalchemy import Column, String, Integer, DateTime

from repository.database import Base


class User(Base):
    """Definition of table User"""
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    birth_date = Column(DateTime)
    sex = Column(String)
    # TODO: subscription plan
