#!/usr/bin/env python3
"""
Import Script - Flytta händelser från lokal databas till Supabase
=================================================================

Läser händelser från familjekalender.db.json och importerar dem till Supabase.

Användning:
    python import_to_supabase.py

Krav:
    - Supabase-konto skapat
    - events-tabell skapad i Supabase
    - SUPABASE_URL och SUPABASE_KEY i .streamlit/secrets.toml
"""

import json
import os
from datetime import datetime

try:
    from supabase import create_client
    import streamlit as st
except ImportError:
    print("❌ Installera dependencies först:")
    print("   pip install supabase streamlit")
    exit(1)


def load_local_events():
    """Läser händelser från JSON backup"""
    json_path = "familjekalender.db.json"

    if not os.path.exists(json_path):
        print(f"❌ Hittade inte {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events = data.get('events', [])
    print(f"✅ Hittade {len(events)} händelser i lokal backup")
    return events


def connect_to_supabase():
    """Ansluter till Supabase med credentials från secrets"""
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")

        if not url or not key:
            print("❌ SUPABASE_URL eller SUPABASE_KEY saknas i .streamlit/secrets.toml")
            print("\nLägg till:")
            print('SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"')
            print('SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"')
            return None

        client = create_client(url, key)
        print(f"✅ Ansluten till Supabase: {url[:30]}...")
        return client

    except Exception as e:
        print(f"❌ Kunde inte ansluta till Supabase: {e}")
        return None


def import_events(client, events):
    """Importerar händelser till Supabase"""
    if not events:
        print("⚠️  Inga händelser att importera")
        return

    print(f"\n📤 Börjar importera {len(events)} händelser...")

    success_count = 0
    error_count = 0

    for i, event in enumerate(events, 1):
        try:
            # Förbered händelse för Supabase (ta bort gamla id och reminder)
            supabase_event = {
                'local_id': event.get('id'),
                'user': event['user'],
                'date': event['date'],
                'time': event['time'],
                'duration': event.get('duration', 1),
                'title': event['title'],
                'description': event.get('description', ''),
                'created_at': event.get('created_at'),
                'repeat_pattern': event.get('repeat_pattern'),
                'repeat_until': event.get('repeat_until')
            }

            # Importera till Supabase
            result = client.table('events').insert(supabase_event).execute()

            print(f"  [{i}/{len(events)}] ✅ {event['user']}: {event['title']} ({event['date']} {event['time']})")
            success_count += 1

        except Exception as e:
            print(f"  [{i}/{len(events)}] ❌ Fel: {event['title']} - {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Import klar!")
    print(f"   - Lyckade: {success_count}")
    print(f"   - Misslyckade: {error_count}")
    print(f"{'='*60}")


def verify_import(client):
    """Verifierar att händelserna finns i Supabase"""
    try:
        result = client.table('events').select('*').execute()
        count = len(result.data)
        print(f"\n🔍 Verifiering: {count} händelser finns nu i Supabase")

        if count > 0:
            print("\nFörsta händelsen i databasen:")
            first = result.data[0]
            print(f"  - ID: {first.get('id')}")
            print(f"  - Användare: {first.get('user')}")
            print(f"  - Titel: {first.get('title')}")
            print(f"  - Datum: {first.get('date')} {first.get('time')}")

        return count
    except Exception as e:
        print(f"❌ Kunde inte verifiera: {e}")
        return 0


def main():
    print("="*60)
    print("📦 Supabase Import Script")
    print("="*60)

    # 1. Läs lokala händelser
    events = load_local_events()
    if not events:
        return

    print(f"\nHändelser att importera:")
    for event in events:
        print(f"  - {event['user']}: {event['title']} ({event['date']})")

    # 2. Anslut till Supabase
    print(f"\n{'='*60}")
    client = connect_to_supabase()
    if not client:
        return

    # 3. Kolla om tabellen redan har data
    try:
        existing = client.table('events').select('id').execute()
        if len(existing.data) > 0:
            print(f"\n⚠️  VARNING: Supabase har redan {len(existing.data)} händelser!")
            response = input("Vill du fortsätta ändå? Detta kan skapa dubbletter. (ja/nej): ")
            if response.lower() not in ['ja', 'j', 'yes', 'y']:
                print("❌ Import avbruten")
                return
    except Exception as e:
        print(f"⚠️  Kunde inte kolla befintliga händelser: {e}")

    # 4. Importera händelser
    print(f"\n{'='*60}")
    import_events(client, events)

    # 5. Verifiera import
    print(f"\n{'='*60}")
    verify_import(client)

    print(f"\n✅ Klart! Gå till Supabase Table Editor för att se dina händelser:")
    print(f"   https://app.supabase.com/project/_/editor")
    print(f"\n💡 Nästa steg: Kör 'streamlit run app.py' för att testa!")


if __name__ == "__main__":
    main()
