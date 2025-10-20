#!/usr/bin/env python3
"""
Inaktivera påminnelser på befintliga händelser
"""

import os
from supabase import create_client, Client

# Konfigurera Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Error: Missing environment variables!")
    print("Please set: SUPABASE_URL and SUPABASE_KEY")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 80)
print("🔕 INAKTIVERA PÅMINNELSER PÅ BEFINTLIGA EVENTS")
print("=" * 80)
print()

# Hämta alla events med reminder=1
response = supabase.table('events').select('*').eq('reminder', 1).execute()

events_with_reminders = response.data

print(f"Hittade {len(events_with_reminders)} events med påminnelser aktiverade:")
print()

for event in events_with_reminders:
    print(f"  🔔 {event['date']} {event['time']} - {event['title']} ({event['user']})")

print()
print("Inaktiverar påminnelser...")
print()

# Uppdatera alla till reminder=0
for event in events_with_reminders:
    supabase.table('events').update({
        'reminder': 0,
        'reminder_sent': False
    }).eq('id', event['id']).execute()

    print(f"  ✅ {event['title']} - påminnelse inaktiverad")

print()
print("=" * 80)
print("✅ KLART!")
print("=" * 80)
print()
print(f"Inaktiverade påminnelser på {len(events_with_reminders)} events.")
print()
print("Framöver kommer endast nya händelser du lägger till med")
print("påminnelse aktiverad att få notiser.")
print()
