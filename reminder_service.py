#!/usr/bin/env python3
"""
Reminder Service - Bakgrundsprocess för Telegram-påminnelser
=============================================================
Körs via GitHub Actions varje minut för att skicka påminnelser
oberoende av om någon använder appen.

Kräver miljövariabler:
- SUPABASE_URL
- SUPABASE_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID_ALBIN
- TELEGRAM_CHAT_ID_MARIA
- TELEGRAM_CHAT_ID_OLLE (valfritt)
- TELEGRAM_CHAT_ID_ELLEN (valfritt)
"""

import os
import sys
from datetime import datetime, timedelta
import requests
from zoneinfo import ZoneInfo

def send_telegram_message(bot_token, chat_id, message):
    """Skickar ett Telegram-meddelande"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")
        return False

def check_and_send_reminders():
    """Huvudfunktion som kollar och skickar påminnelser"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for reminders...")

    # Hämta miljövariabler
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not all([supabase_url, supabase_key, bot_token]):
        print("[ERROR] Missing required environment variables!")
        print(f"  SUPABASE_URL: {'✓' if supabase_url else '✗'}")
        print(f"  SUPABASE_KEY: {'✓' if supabase_key else '✗'}")
        print(f"  TELEGRAM_BOT_TOKEN: {'✓' if bot_token else '✗'}")
        return 1

    try:
        from supabase import create_client

        # Anslut till Supabase
        supabase = create_client(supabase_url, supabase_key)
        print("[SUPABASE] Connected successfully")

        # Hämta nuvarande tid i svensk tidszon (Europe/Stockholm)
        # GitHub Actions körs på UTC, men våra händelser är i svensk tid
        stockholm_tz = ZoneInfo("Europe/Stockholm")
        now = datetime.now(stockholm_tz)
        today = now.strftime('%Y-%m-%d')

        # Tidsfönster: 14-16 minuter framåt
        reminder_time_start = now + timedelta(minutes=14)
        reminder_time_end = now + timedelta(minutes=16)

        print(f"[TIME] Current time (Stockholm): {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"[TIME] Looking for events between {reminder_time_start.strftime('%H:%M')} and {reminder_time_end.strftime('%H:%M')}")

        # Hämta events med påminnelse som inte skickats
        # OBS: Supabase kan ha reminder som både 0/1 (integer) eller True/False (boolean)
        # Hämta alla events idag och filtrera i Python för maximal kompatibilitet
        response = supabase.table('events').select('*').eq('date', today).execute()

        # Filtrera: reminder måste vara aktiverad (1, True, eller "truthy")
        # OCH reminder_sent måste vara False/0/None
        events = []
        for e in response.data:
            reminder = e.get('reminder')
            reminder_sent = e.get('reminder_sent')

            # reminder måste vara aktiverad (hantera både 0/1 och True/False)
            if reminder in (1, True, '1'):
                # reminder_sent måste vara False/0/None (hantera både 0/1 och True/False)
                if reminder_sent in (0, False, None, '0'):
                    events.append(e)

        print(f"[EVENTS] Total events today: {len(response.data)}")
        print(f"[EVENTS] Events with unsent reminders: {len(events)}")

        if len(response.data) > 0 and len(events) == 0:
            print(f"[DEBUG] All events today already have reminders sent or reminder disabled")
            # Visa exempel på första eventet för debugging
            if response.data:
                first = response.data[0]
                print(f"[DEBUG] Example event: reminder={first.get('reminder')}, reminder_sent={first.get('reminder_sent')}")

        reminders_sent = 0

        for event in events:
            event_time_str = event['time']
            # Skapa datetime i svensk tidszon
            event_datetime = datetime.strptime(f"{today} {event_time_str}", '%Y-%m-%d %H:%M')
            event_datetime = event_datetime.replace(tzinfo=stockholm_tz)

            # Kolla om eventet är i påminnelsefönstret
            if reminder_time_start <= event_datetime <= reminder_time_end:
                user = event['user']
                title = event['title']

                print(f"[MATCH] Event '{title}' for {user} at {event_time_str} is in reminder window")

                # Hämta chat ID för användaren
                chat_id_key = f"TELEGRAM_CHAT_ID_{user.upper()}"
                chat_id = os.getenv(chat_id_key)

                if not chat_id:
                    print(f"[SKIP] No Telegram chat ID configured for {user} ({chat_id_key})")
                    continue

                # Skapa meddelande
                message = f"""📅 *Påminnelse: {title}*

🕐 Börjar om 15 minuter ({event_time_str})
👤 {user}
📆 {today}

God förberedelse! 🙂"""

                # Skicka påminnelse
                if send_telegram_message(bot_token, chat_id, message):
                    print(f"[SENT] Reminder sent to {user}")

                    # Markera som skickad i Supabase (använd 1 för konsistens)
                    supabase.table('events').update({'reminder_sent': 1}).eq('id', event['id']).execute()
                    print(f"[UPDATE] Marked event {event['id']} as reminder_sent=1")

                    reminders_sent += 1
                else:
                    print(f"[FAILED] Could not send reminder to {user}")

        print(f"[SUMMARY] Sent {reminders_sent} reminder(s)")
        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(check_and_send_reminders())
