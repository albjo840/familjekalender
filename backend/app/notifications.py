import requests
import os
from datetime import datetime, timedelta
from typing import Optional

NTFY_URL = os.getenv("NTFY_URL", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "familjekalender")

def send_notification(
    title: str,
    message: str,
    priority: str = "default",
    tags: Optional[list] = None
):
    """
    Skicka en notifikation via ntfy.sh

    Args:
        title: Notifikationens titel
        message: Notifikationens meddelande
        priority: Prioritet (max, high, default, low, min)
        tags: Lista med emoji-tags för notifikationen
    """
    try:
        headers = {
            "Title": title,
            "Priority": priority,
        }

        if tags:
            headers["Tags"] = ",".join(tags)

        response = requests.post(
            f"{NTFY_URL}/{NTFY_TOPIC}",
            data=message.encode('utf-8'),
            headers=headers
        )

        return response.status_code == 200
    except Exception as e:
        print(f"Fel vid skickning av notifikation: {e}")
        return False

def send_event_reminder(event_title: str, event_start: datetime, user_name: str):
    """
    Skicka påminnelse om en kommande händelse
    """
    time_until = event_start - datetime.utcnow()

    if time_until.total_seconds() > 60:
        minutes = int(time_until.total_seconds() / 60)
        time_str = f"{minutes} minuter"
    else:
        time_str = "snart"

    title = f"Påminnelse: {event_title}"
    message = f"{user_name} har en händelse om {time_str}"

    return send_notification(
        title=title,
        message=message,
        priority="high",
        tags=["calendar", "alarm_clock"]
    )

def send_event_created(event_title: str, user_name: str):
    """
    Skicka notifikation när en ny händelse skapas
    """
    title = "Ny händelse tillagd"
    message = f"{user_name}: {event_title}"

    return send_notification(
        title=title,
        message=message,
        tags=["calendar", "white_check_mark"]
    )
