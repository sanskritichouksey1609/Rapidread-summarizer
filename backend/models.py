from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
import datetime


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    source_id = Column(String, index=True, nullable=True)
    content = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
