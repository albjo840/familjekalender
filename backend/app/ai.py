"""
AI Assistant för Familjekalender med Groq integration
Hanterar konversationer och bokningar med dedupliceringssystem
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy.orm import Session

from . import crud, schemas

# Ladda environment variables från .env
load_dotenv()

# Dedupliceringssystem: Håller koll på vilka bokningar som redan skapats
# Key: session_id + event_hash, Value: event_id
_CREATED_EVENTS_CACHE: Dict[str, int] = {}

# Timeout för cache-entries (10 minuter)
_CACHE_TIMEOUT = 600
_CACHE_TIMESTAMPS: Dict[str, float] = {}


def _clean_old_cache_entries():
    """Rensa gamla cache-entries för att undvika minnesläckor"""
    current_time = datetime.now().timestamp()
    keys_to_remove = [
        key for key, timestamp in _CACHE_TIMESTAMPS.items()
        if current_time - timestamp > _CACHE_TIMEOUT
    ]
    for key in keys_to_remove:
        _CREATED_EVENTS_CACHE.pop(key, None)
        _CACHE_TIMESTAMPS.pop(key, None)


def _create_event_hash(event_data: Dict[str, Any]) -> str:
    """
    Skapa en unik hash för en händelse baserat på dess attribut
    Hash baseras på: normaliserad titel, starttid (datum+timme), användar-ID och varaktighet
    """
    # Normalisera titel: lowercase och ta bort extra whitespace
    title = event_data.get('title', '').lower().strip()

    # Extrahera starttid och sluttid
    start_time = event_data.get('start_time', '')
    end_time = event_data.get('end_time', '')

    # Om start_time är en sträng, extrahera bara datum och timme (ignorera minuter för flexibilitet)
    if isinstance(start_time, str):
        # Ta första 13 tecken: "2024-11-08T12" (datum och timme)
        start_time = start_time[:13] if len(start_time) >= 13 else start_time

    user_id = event_data.get('user_id', '')

    # Skapa hash: normaliserad titel + datum/timme + user_id
    # Detta fångar "samma bokning" även om titeln varierar lite
    hash_str = f"{start_time}|{user_id}"
    return hash_str


def _check_duplicate_event(session_id: str, event_data: Dict[str, Any]) -> Optional[int]:
    """
    Kontrollera om denna händelse redan har skapats i denna session
    Returnerar event_id om den redan finns, None annars
    """
    _clean_old_cache_entries()
    event_hash = _create_event_hash(event_data)
    cache_key = f"{session_id}:{event_hash}"
    return _CREATED_EVENTS_CACHE.get(cache_key)


def _mark_event_created(session_id: str, event_data: Dict[str, Any], event_id: int):
    """Markera att en händelse har skapats för att förhindra dubletter"""
    event_hash = _create_event_hash(event_data)
    cache_key = f"{session_id}:{event_hash}"
    _CREATED_EVENTS_CACHE[cache_key] = event_id
    _CACHE_TIMESTAMPS[cache_key] = datetime.now().timestamp()


# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Verktyg som AI:n kan använda
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Hämta kalenderhändelser för en viss tidsperiod. Använd detta för att se vad som är bokat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Startdatum i ISO format (YYYY-MM-DD), t.ex. '2024-01-15'. Om inte angivet, använd idag."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Slutdatum i ISO format (YYYY-MM-DD), t.ex. '2024-01-20'. Om inte angivet, använd en vecka framåt."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Skapa en ny kalenderhändelse. VIKTIGT: Anropa endast EN gång per bokning!",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Händelsens titel/rubrik"
                    },
                    "description": {
                        "type": "string",
                        "description": "Beskrivning av händelsen (valfritt)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Starttid i ISO format med tid (YYYY-MM-DDTHH:MM:SS), t.ex. '2024-01-15T14:00:00'"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "Sluttid i ISO format med tid (YYYY-MM-DDTHH:MM:SS), t.ex. '2024-01-15T16:00:00'"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "Användarens ID (1=albin, 2=maria, 3=olle, 4=ellen, 5=familj)"
                    },
                    "all_day": {
                        "type": "boolean",
                        "description": "Sant om det är en heldagshändelse, annars falskt"
                    }
                },
                "required": ["title", "start_time", "end_time", "user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_users",
            "description": "Hämta alla användare i familjen med deras ID och färger",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def get_events_tool(db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """Verktyg: Hämta händelser från databasen"""
    try:
        # Default värden
        if not start_date:
            start_dt = datetime.now()
        else:
            start_dt = datetime.fromisoformat(start_date)

        if not end_date:
            end_dt = start_dt + timedelta(days=7)
        else:
            end_dt = datetime.fromisoformat(end_date)

        events = crud.get_events(db, start_date=start_dt, end_date=end_dt, limit=100)

        if not events:
            return "Inga händelser hittades för den valda tidsperioden."

        result = []
        for event in events:
            result.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "user": event.owner.name,
                "user_id": event.user_id
            })

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return f"Fel vid hämtning av händelser: {str(e)}"


def create_event_tool(
    db: Session,
    session_id: str,
    title: str,
    start_time: str,
    end_time: str,
    user_id: int,
    description: Optional[str] = None,
    all_day: bool = False
) -> str:
    """
    Verktyg: Skapa en ny händelse med dedupliceringskontroll
    VIKTIGT: Kontrollerar om händelsen redan skapats i denna session
    """
    try:
        # Skapa event data
        event_data = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "user_id": user_id,
            "description": description,
            "all_day": all_day
        }

        # DEDUPLICERINGSKONTROLL
        existing_event_id = _check_duplicate_event(session_id, event_data)
        if existing_event_id:
            return json.dumps({
                "success": True,
                "message": "Händelsen är redan skapad (dublettskydd aktivt)",
                "event_id": existing_event_id,
                "duplicate": True
            }, ensure_ascii=False)

        # Verifiera användare
        user = crud.get_user(db, user_id=user_id)
        if not user:
            return json.dumps({
                "success": False,
                "error": f"Användare med ID {user_id} finns inte"
            }, ensure_ascii=False)

        # Konvertera till datetime
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)

        # Skapa händelsen
        event_create = schemas.EventCreate(
            title=title,
            description=description or "",
            start_time=start_dt,
            end_time=end_dt,
            all_day=all_day,
            user_id=user_id,
            reminder_enabled=False,
            reminder_minutes=30
        )

        db_event = crud.create_event(db=db, event=event_create)

        # Markera som skapad i cache
        _mark_event_created(session_id, event_data, db_event.id)

        return json.dumps({
            "success": True,
            "message": f"Händelsen '{title}' har skapats för {user.name}",
            "event_id": db_event.id,
            "user": user.name,
            "duplicate": False
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Fel vid skapande av händelse: {str(e)}"
        }, ensure_ascii=False)


def get_users_tool(db: Session) -> str:
    """Verktyg: Hämta alla användare"""
    try:
        users = crud.get_users(db, limit=100)
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "name": user.name,
                "color": user.color
            })
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Fel vid hämtning av användare: {str(e)}"


def handle_tool_call(tool_call: Any, db: Session, session_id: str) -> str:
    """Hantera verktygsanrop från AI:n"""
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "get_events":
        return get_events_tool(
            db,
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date")
        )

    elif function_name == "create_event":
        return create_event_tool(
            db,
            session_id=session_id,
            title=arguments["title"],
            start_time=arguments["start_time"],
            end_time=arguments["end_time"],
            user_id=arguments["user_id"],
            description=arguments.get("description"),
            all_day=arguments.get("all_day", False)
        )

    elif function_name == "get_users":
        return get_users_tool(db)

    else:
        return f"Okänt verktyg: {function_name}"


def chat_with_ai(
    message: str,
    db: Session,
    session_id: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Huvudfunktion för att chatta med AI:n

    Args:
        message: Användarens meddelande
        db: Databassession
        session_id: Unik session ID för dedupliceringskontroll
        conversation_history: Tidigare konversation (valfritt)

    Returns:
        Dict med AI:ns svar och uppdaterad konversationshistorik
    """
    try:
        # Bygg konversation
        if conversation_history is None:
            conversation_history = []

        # System prompt
        system_message = {
            "role": "system",
            "content": f"""Du är en AI-assistent för familjekalender.
Idag är {datetime.now().strftime('%Y-%m-%d')}.

Användare i systemet:
- albin (ID: 1, blå)
- maria (ID: 2, röd)
- olle (ID: 3, gul)
- ellen (ID: 4, lila)
- familj (ID: 5, grön)

Du kan:
1. Svara på frågor om vad som är bokat
2. Skapa nya bokningar

VIKTIGT REGLER FÖR BOKNINGAR:
- När du skapar en bokning, anropa create_event ENDAST EN GÅNG
- Om användaren säger "boka", skapa bara EN händelse
- Bekräfta alltid vilken användare bokningen är för
- Använd svenskt datumformat när du pratar med användaren
- Var kortfattad och trevlig

Dedupliceringssystem är aktivt - om du försöker skapa samma händelse flera gånger kommer den bara skapas en gång."""
        }

        messages = [system_message] + conversation_history + [{"role": "user", "content": message}]

        # Första AI-anropet
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1000,
            temperature=0.1  # Lägre temperatur för mer konsekventa function calls
        )

        assistant_message = response.choices[0].message
        tool_calls = getattr(assistant_message, 'tool_calls', None)

        # Om AI:n vill använda verktyg
        if tool_calls:
            # Lägg till AI:ns svar i historiken
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            # Exekvera verktygsanrop
            for tool_call in tool_calls:
                tool_result = handle_tool_call(tool_call, db, session_id)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result
                })

            # Andra AI-anropet med verktygsresultat
            second_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=1000
            )

            final_message = second_response.choices[0].message.content
        else:
            # Inget verktygsanrop, använd direktsvaret
            final_message = assistant_message.content

        # Uppdatera konversationshistorik (spara bara user/assistant, inte system/tool)
        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": final_message}
        ]

        # Begränsa historik till senaste 10 meddelandena för att spara tokens
        if len(updated_history) > 10:
            updated_history = updated_history[-10:]

        return {
            "success": True,
            "message": final_message,
            "conversation_history": updated_history
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Fel i AI-chat: {str(e)}",
            "message": "Tyvärr uppstod ett fel. Försök igen senare."
        }
