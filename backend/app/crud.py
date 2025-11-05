from sqlalchemy.orm import Session
from . import models, schemas
from .recurrence import generate_recurrence_instances
from datetime import datetime, timedelta
from typing import Optional, List

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, color=user.color)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Event CRUD operations
def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events(db: Session, skip: int = 0, limit: int = 1000, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """
    Hämta events inklusive återkommande instanser
    """
    # Om inget datumintervall är angivet, använd de senaste 3 månaderna till 6 månader framåt
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=90)
    if not end_date:
        end_date = datetime.utcnow() + timedelta(days=180)

    # Hämta alla events som potentiellt kan visa sig i intervallet
    # Inkludera recurring events som startade innan end_date
    query = db.query(models.Event).filter(
        models.Event.start_time <= end_date
    )

    all_events = query.all()

    # Samla alla event-instanser (original + recurring)
    result_events = []

    for event in all_events:
        # Lägg till original händelsen om den är inom intervallet
        if event.start_time >= start_date and event.start_time <= end_date:
            result_events.append(event)

        # Om händelsen är återkommande, generera instanser
        if event.recurrence_type != "none":
            recurring_instances = generate_recurrence_instances(event, start_date, end_date)
            result_events.extend(recurring_instances)

    return result_events

def get_events_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Event).filter(models.Event.user_id == user_id).offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event_update: schemas.EventUpdate):
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)

    db_event.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = get_event(db, event_id)
    if db_event:
        db.delete(db_event)
        db.commit()
        return True
    return False
