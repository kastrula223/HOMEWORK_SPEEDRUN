from sqlalchemy import Column, Integer, String
from database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    event = Column(String(200), nullable=False, index=True)
    age = Column(Integer, nullable=False)