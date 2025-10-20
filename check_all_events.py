#!/usr/bin/env python3
"""
Kollar alla events i Supabase och visar deras reminder-status
"""

import os
from datetime import datetime
from supabase import create_client, Client

# Konfigurera Supabase
supabase_url = os.getenv('SUPABASE_URL', 'https://***REMOVED***')
supabase_key = os.getenv('SUPABASE_KEY', '***REMOVED***')

supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 80)
print("📅 ALLA EVENTS I SUPABASE")
print("=" * 80)
print()

# Hämta alla events
response = supabase.table('events').select('*').order('date', desc=False).execute()

events = response.data
print(f"Totalt: {len(events)} events")
print()

# Gruppera per datum
from collections import defaultdict
events_by_date = defaultdict(list)

for event in events:
    events_by_date[event['date']].append(event)

# Visa per datum
for date in sorted(events_by_date.keys()):
    print(f"📆 {date}")
    print("-" * 80)

    for event in events_by_date[date]:
        reminder = event.get('reminder', 0)
        reminder_sent = event.get('reminder_sent', False)

        reminder_icon = "🔔" if reminder else "🔕"
        sent_status = " (✅ skickad)" if reminder_sent else " (⏳ väntar)" if reminder else ""

        print(f"  {reminder_icon} {event['time']:5} - {event['title']:30} ({event['user']:10}) {sent_status}")

    print()

# Statistik
total_with_reminder = sum(1 for e in events if e.get('reminder', 0))
total_sent = sum(1 for e in events if e.get('reminder_sent', False))

print("=" * 80)
print("📊 STATISTIK")
print("=" * 80)
print(f"  Totalt events: {len(events)}")
print(f"  Med påminnelse (reminder=1): {total_with_reminder}")
print(f"  Påminnelser skickade (reminder_sent=1): {total_sent}")
print(f"  Påminnelser väntar: {total_with_reminder - total_sent}")
print()

# Dagens events
now = datetime.now()
today = now.strftime('%Y-%m-%d')
todays_events = events_by_date.get(today, [])
todays_reminders = [e for e in todays_events if e.get('reminder', 0)]

print(f"🕐 Idag ({today}):")
print(f"  - {len(todays_events)} events")
print(f"  - {len(todays_reminders)} med påminnelse")
print()

if len(todays_reminders) == 0:
    print("💡 TIP:")
    print("  För att testa påminnelser, lägg till en händelse om 20-30 minuter")
    print("  med påminnelse aktiverad i kalendern.")
    print()
