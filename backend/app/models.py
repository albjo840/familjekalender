from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # albin, maria, olle, ellen, familj
    color = Column(String)  # Hex color code för användaren
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="owner")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    all_day = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    reminder_enabled = Column(Boolean, default=False)
    reminder_minutes = Column(Integer, default=30)  # Påminnelse X minuter innan
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="events")
