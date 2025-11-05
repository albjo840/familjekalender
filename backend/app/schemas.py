from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    name: str
    color: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    user_id: int
    reminder_enabled: bool = False
    reminder_minutes: int = 30

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    user_id: Optional[int] = None
    reminder_enabled: Optional[bool] = None
    reminder_minutes: Optional[int] = None

class Event(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner: User

    class Config:
        from_attributes = True
