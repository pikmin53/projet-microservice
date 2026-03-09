from fastapi import HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Float, DateTime, Interval, Text, VARCHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime


DATABASE_API_URL = os.getenv("DATABASE_API_URL")
engine = create_engine(DATABASE_API_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    service = Column(VARCHAR(100), nullable=False)
    level = Column(VARCHAR(100), nullable=False)
    message = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)


Base.metadata.create_all(bind=engine)


# API MODELS
class LogCreate(BaseModel):
    service: str
    level: str
    message: str
    time: datetime.datetime

