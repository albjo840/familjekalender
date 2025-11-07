from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import models, schemas, crud, notifications, ai
from .database import engine, get_db

# Databas-tabeller skapas via init_users.py
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Familjekalender API")

# CORS middleware för React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # I produktion, specificera exakt origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servera React build i produktion
# app.mount("/static", StaticFiles(directory="static"), name="static")

# User endpoints
@app.get("/api/users", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/api/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/api/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.create_user(db=db, user=user)

# Event endpoints
@app.get("/api/events", response_model=List[schemas.Event])
def read_events(
    skip: int = 0,
    limit: int = 1000,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    events = crud.get_events(db, skip=skip, limit=limit, start_date=start_dt, end_date=end_dt)
    return events

@app.get("/api/events/{event_id}", response_model=schemas.Event)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@app.post("/api/events", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    # Verifiera att användaren finns
    user = crud.get_user(db, user_id=event.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_event = crud.create_event(db=db, event=event)

    # Skicka notifikation om ny händelse
    notifications.send_event_created(
        event_title=db_event.title,
        user_name=user.name
    )

    return db_event

@app.put("/api/events/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    db_event = crud.update_event(db, event_id=event_id, event_update=event)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@app.delete("/api/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    success = crud.delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}

# Webhook endpoint
@app.post("/webhook")
async def receive_webhook(data: dict):
    """
    Webhook endpoint för att ta emot externa notifikationer
    """
    # Här kan du lägga till logik för att hantera webhooks
    # t.ex. från externa kalendersystem
    return {"status": "ok", "received": data}

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Migration endpoint (körs en gång för att uppdatera databas-schema)
@app.post("/admin/migrate")
def run_migration(db: Session = Depends(get_db)):
    """
    Kör databas-migration för att lägga till recurrence-kolumner
    Säkert att köra flera gånger (IF NOT EXISTS)
    """
    from sqlalchemy import text
    results = []

    try:
        db.execute(text("""
            ALTER TABLE events
            ADD COLUMN IF NOT EXISTS recurrence_type VARCHAR DEFAULT 'none'
        """))
        db.commit()
        results.append("✓ recurrence_type")
    except Exception as e:
        results.append(f"recurrence_type: {str(e)}")

    try:
        db.execute(text("""
            ALTER TABLE events
            ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1
        """))
        db.commit()
        results.append("✓ recurrence_interval")
    except Exception as e:
        results.append(f"recurrence_interval: {str(e)}")

    try:
        db.execute(text("""
            ALTER TABLE events
            ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP
        """))
        db.commit()
        results.append("✓ recurrence_end_date")
    except Exception as e:
        results.append(f"recurrence_end_date: {str(e)}")

    return {"status": "migration completed", "results": results}

# AI Chat endpoint
@app.post("/api/ai/chat", response_model=schemas.ChatResponse)
def chat_with_assistant(chat_request: schemas.ChatRequest, db: Session = Depends(get_db)):
    """
    Chat med AI-assistenten om kalenderhändelser

    AI:n kan:
    - Svara på frågor om bokningar
    - Skapa nya bokningar
    - Visa vad som är bokat för olika familjemedlemmar

    VIKTIGT: session_id används för att förhindra multipla bokningar
    """
    # Konvertera ChatMessage objekt till dict för AI-funktionen
    history = [{"role": msg.role, "content": msg.content} for msg in chat_request.conversation_history]

    result = ai.chat_with_ai(
        message=chat_request.message,
        db=db,
        session_id=chat_request.session_id,
        conversation_history=history
    )

    # Konvertera tillbaka till ChatMessage objekt
    conv_history = [schemas.ChatMessage(role=msg["role"], content=msg["content"])
                    for msg in result.get("conversation_history", [])]

    return schemas.ChatResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        conversation_history=conv_history,
        error=result.get("error")
    )

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Familjekalender API", "version": "1.0.0"}
