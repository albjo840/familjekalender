#!/usr/bin/env python3
"""
Test Supabase connection and table structure
"""
import os
from supabase import create_client

# Använd environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("=" * 60)
print("SUPABASE CONNECTION TEST")
print("=" * 60)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ SUPABASE credentials saknas!")
    print(f"  SUPABASE_URL: {'✓' if SUPABASE_URL else '✗'}")
    print(f"  SUPABASE_KEY: {'✓' if SUPABASE_KEY else '✗'}")
    exit(1)

try:
    # Anslut till Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Anslutning till Supabase lyckades!")

    # Hämta alla events
    response = supabase.table('events').select('*').limit(5).execute()

    print(f"\n📊 Hittade {len(response.data)} händelser (visar max 5)")

    if response.data:
        print("\n🔍 Första händelsen:")
        first_event = response.data[0]
        for key, value in first_event.items():
            print(f"  {key}: {value}")

        # Kolla om reminder-kolumner finns
        print("\n📋 Kolumn-check:")
        has_reminder = 'reminder' in first_event
        has_reminder_sent = 'reminder_sent' in first_event

        print(f"  reminder kolumn: {'✅' if has_reminder else '❌ SAKNAS!'}")
        print(f"  reminder_sent kolumn: {'✅' if has_reminder_sent else '❌ SAKNAS!'}")

        if not has_reminder or not has_reminder_sent:
            print("\n⚠️  PROBLEM HITTAT: Supabase-tabellen saknar påminnelsekolumner!")
            print("    Detta måste fixas för att påminnelser ska fungera.")
    else:
        print("\n⚠️  Inga händelser i databasen - kan inte kolla kolumner")

except Exception as e:
    print(f"❌ Fel: {e}")
    import traceback
    traceback.print_exc()
