#!/usr/bin/env python3
"""
Fix Supabase table - lägg till reminder_sent kolumn
"""
from supabase import create_client

SUPABASE_URL = 'https://***REMOVED***'
SUPABASE_KEY = '***REMOVED***'

print("=" * 60)
print("FIXING SUPABASE TABLE")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Supabase använder PostgreSQL, så vi kör SQL direkt
    # OBS: Detta kräver att vi har tillgång till PostgreSQL via Supabase
    # Alternativt måste det göras via Supabase Dashboard

    print("\n⚠️  VIKTIGT:")
    print("Supabase-tabellen saknar kolumnen 'reminder_sent'.")
    print("\nDu måste lägga till den via Supabase Dashboard:")
    print("\n1. Gå till: https://supabase.com/dashboard/project/xbhqtqjriiytkcnprteb/editor")
    print("2. Välj 'events' tabellen")
    print("3. Klicka på 'New Column' eller gå till SQL Editor")
    print("4. Kör denna SQL:")
    print("\n" + "─" * 60)
    print("ALTER TABLE events ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;")
    print("─" * 60)
    print("\nEller använd RPC om tillgängligt...")

    # Försök via RPC (om du har skapat en stored procedure)
    # Detta fungerar INTE utan att du först skapat funktionen i Supabase

except Exception as e:
    print(f"\n❌ Fel: {e}")
