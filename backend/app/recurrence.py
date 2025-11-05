"""
Logik för att hantera återkommande händelser
"""
from datetime import datetime, timedelta
from typing import List, Dict
from . import models

def generate_recurrence_instances(event: models.Event, start_date: datetime, end_date: datetime) -> List[Dict]:
    """
    Generera alla instanser av en återkommande händelse inom ett datumintervall

    Args:
        event: Händelsen med recurrence information
        start_date: Start för intervall att generera instanser för
        end_date: Slut för intervall att generera instanser för

    Returns:
        Lista med dictionaries för varje händelse-instans
    """
    if event.recurrence_type == "none":
        return []

    instances = []

    # Beräkna duration av original händelse
    duration = event.end_time - event.start_time

    # Start från original händelsens start
    current_start = event.start_time

    # Om händelsen har ett slut-datum för upprepning, använd det
    # Annars generera upp till 1 år framåt
    max_date = event.recurrence_end_date if event.recurrence_end_date else end_date

    # Begränsa till max 1000 instanser för säkerhet
    max_instances = 1000
    instance_count = 0

    while current_start <= max_date and current_start <= end_date and instance_count < max_instances:
        # Hoppa över original händelsen (den finns redan i databasen)
        if current_start != event.start_time:
            # Kolla om denna instans är inom det begärda intervallet
            if current_start >= start_date:
                current_end = current_start + duration
                instances.append({
                    "id": f"{event.id}_r_{instance_count}",  # Unikt ID för recurring instance
                    "title": event.title,
                    "description": event.description,
                    "start_time": current_start.isoformat(),
                    "end_time": current_end.isoformat(),
                    "all_day": event.all_day,
                    "user_id": event.user_id,
                    "reminder_enabled": event.reminder_enabled,
                    "reminder_minutes": event.reminder_minutes,
                    "recurrence_type": event.recurrence_type,
                    "recurrence_interval": event.recurrence_interval,
                    "recurrence_end_date": event.recurrence_end_date.isoformat() if event.recurrence_end_date else None,
                    "created_at": event.created_at.isoformat(),
                    "updated_at": event.updated_at.isoformat(),
                    "owner": {
                        "id": event.owner.id,
                        "name": event.owner.name,
                        "color": event.owner.color,
                        "created_at": event.owner.created_at.isoformat()
                    },
                    "is_recurring_instance": True,
                    "parent_event_id": event.id
                })
                instance_count += 1

        # Beräkna nästa instans baserat på recurrence_type
        if event.recurrence_type == "daily":
            current_start += timedelta(days=event.recurrence_interval)
        elif event.recurrence_type == "weekly":
            current_start += timedelta(weeks=event.recurrence_interval)
        elif event.recurrence_type == "monthly":
            # För månadsvis upprepning, lägg till månader
            month = current_start.month + event.recurrence_interval
            year = current_start.year

            while month > 12:
                month -= 12
                year += 1

            # Hantera edge case om dagen inte finns i den nya månaden (t.ex. 31 feb)
            try:
                current_start = current_start.replace(year=year, month=month)
            except ValueError:
                # Om dagen inte finns (t.ex. 31 feb), använd sista dagen i månaden
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year
                current_start = datetime(next_year, next_month, 1) - timedelta(days=1)
                current_start = current_start.replace(
                    hour=event.start_time.hour,
                    minute=event.start_time.minute,
                    second=event.start_time.second
                )

    return instances
