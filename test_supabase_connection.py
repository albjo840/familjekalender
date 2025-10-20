#!/usr/bin/env python3
"""
Test Supabase Connection
========================
Verifierar att händelser kan hämtas från Supabase
"""

import streamlit as st
from supabase import create_client

print("="*60)
print("🔍 Testar Supabase-anslutning...")
print("="*60)

# Hämta credentials
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")

if not url or not key:
    print("❌ SUPABASE_URL eller SUPABASE_KEY saknas i secrets")
    exit(1)

print(f"✅ Credentials hittade")
print(f"   URL: {url[:40]}...")

# Anslut
try:
    client = create_client(url, key)
    print("✅ Ansluten till Supabase")
except Exception as e:
    print(f"❌ Kunde inte ansluta: {e}")
    exit(1)

# Hämta händelser
try:
    response = client.table('events').select('*').execute()
    events = response.data

    print(f"\n✅ Hittade {len(events)} händelser i molnet!")
    print("\nHändelser från Supabase:")
    print("-" * 60)

    for event in events:
        print(f"  • {event['user']}: {event['title']}")
        print(f"    Datum: {event['date']} {event['time']}")
        if event.get('repeat_pattern'):
            print(f"    Återkommer: {event['repeat_pattern']} till {event.get('repeat_until')}")
        print()

    print("="*60)
    print("✅ Supabase fungerar perfekt!")
    print("="*60)

except Exception as e:
    print(f"❌ Kunde inte hämta händelser: {e}")
    exit(1)
