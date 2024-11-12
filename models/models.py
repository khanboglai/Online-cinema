from sqlalchemy import Column, Integer, String
from repository.database import Base

# table 'User' definition
class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)