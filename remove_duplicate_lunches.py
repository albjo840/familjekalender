#!/usr/bin/env python3
"""
Ta bort duplicerade lunch-bokningar för Maria 2025-10-21
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
print("🗑️  TA BORT DUPLICERADE LUNCH-BOKNINGAR FÖR MARIA")
print("=" * 80)
print()

# Hämta alla lunch-events för Maria den 2025-10-21
response = supabase.table('events').select('*').eq('user', 'Maria').eq('date', '2025-10-21').eq('title', 'Lunch').eq('time', '12:00').execute()

lunch_events = response.data

print(f"Hittade {len(lunch_events)} lunch-bokningar för Maria den 2025-10-21 kl 12:00")
print()

if len(lunch_events) == 0:
    print("Inga dubletter hittades!")
    exit(0)

if len(lunch_events) == 1:
    print("Bara en lunch-bokning finns - ingen duplicering!")
    exit(0)

print("📋 Alla hittade bokningar:")
for i, event in enumerate(lunch_events, 1):
    print(f"  {i}. ID: {event['id']} - {event['title']} ({event['time']}) - Created: {event.get('created_at', 'N/A')}")

print()
print(f"Behåller den FÖRSTA bokningen (ID: {lunch_events[0]['id']})")
print(f"Tar bort {len(lunch_events) - 1} duplicerade bokningar...")
print()

# Ta bort alla utom den första
deleted_count = 0
for event in lunch_events[1:]:  # Skippa första (index 0)
    try:
        supabase.table('events').delete().eq('id', event['id']).execute()
        print(f"  ✅ Raderade ID: {event['id']}")
        deleted_count += 1
    except Exception as e:
        print(f"  ❌ Kunde inte radera ID {event['id']}: {e}")

print()
print("=" * 80)
print("✅ KLART!")
print("=" * 80)
print()
print(f"Totalt {deleted_count} duplicerade lunch-bokningar borttagna.")
print(f"Kvar: 1 lunch-bokning för Maria den 2025-10-21 kl 12:00")
print()
