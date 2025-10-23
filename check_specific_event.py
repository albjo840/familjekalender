#!/usr/bin/env python3
"""
Kollar en specifik händelse för att se om den kommer få påminnelse
"""
import os
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

try:
    from supabase import create_client
except ImportError:
    print("❌ Supabase not installed. Run: pip install supabase")
    sys.exit(1)

def check_event():
    print("=" * 60)
    print("KOLLAR HÄNDELSE: 'test 2' för Albin kl 10:20")
    print("=" * 60)
    print()

    # Hämta credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Miljövariabler saknas!")
        print("   Kör: export SUPABASE_URL='...' SUPABASE_KEY='...'")
        print()
        print("   Eller lägg till i .streamlit/secrets.toml")
        return False

    # Anslut till Supabase
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Ansluten till Supabase")
    print()

    # Svensk tidszon
    stockholm_tz = ZoneInfo("Europe/Stockholm")
    now = datetime.now(stockholm_tz)
    today = now.strftime('%Y-%m-%d')

    print(f"📅 Datum idag: {today}")
    print(f"🕐 Tid nu: {now.strftime('%H:%M:%S')}")
    print()

    # Sök efter händelsen
    response = supabase.table('events').select('*').eq('date', today).eq('user', 'Albin').eq('time', '10:20').execute()

    if not response.data:
        print("❌ Hittade ingen händelse för Albin kl 10:20 idag")
        print()
        print("Möjliga orsaker:")
        print("  - Händelsen är inte i Supabase (bara i lokal SQLite)")
        print("  - Tiden är inte exakt '10:20'")
        print("  - Datumet är fel")
        print()

        # Visa alla händelser för Albin idag
        all_albin = supabase.table('events').select('*').eq('date', today).eq('user', 'Albin').execute()
        if all_albin.data:
            print(f"Händelser för Albin idag ({len(all_albin.data)}):")
            for e in all_albin.data:
                print(f"  - {e['time']} | {e['title']} | reminder={e.get('reminder')} | reminder_sent={e.get('reminder_sent')}")
        else:
            print("Inga händelser för Albin idag i Supabase")

        return False

    event = response.data[0]

    print("✅ HÄNDELSE HITTAD:")
    print(f"  ID: {event['id']}")
    print(f"  Titel: {event['title']}")
    print(f"  Användare: {event['user']}")
    print(f"  Datum: {event['date']}")
    print(f"  Tid: {event['time']}")
    print(f"  reminder: {event.get('reminder')} (typ: {type(event.get('reminder')).__name__})")
    print(f"  reminder_sent: {event.get('reminder_sent')} (typ: {type(event.get('reminder_sent')).__name__})")
    print()

    # Analysera om påminnelse kommer skickas
    reminder = event.get('reminder')
    reminder_sent = event.get('reminder_sent')

    print("ANALYS:")
    print("-" * 60)

    # Kolla om reminder är aktiverad
    if reminder in (1, True, '1'):
        print("✅ Påminnelse är AKTIVERAD")
    else:
        print(f"❌ Påminnelse är INTE aktiverad (värde: {reminder})")
        print()
        print("FIX: Redigera händelsen och aktivera påminnelse")
        print("     Eller skapa en ny händelse med påminnelse aktiverad")
        return False

    # Kolla om reminder_sent är 0/False/None
    if reminder_sent in (0, False, None, '0'):
        print("✅ Påminnelse är INTE redan skickad")
    else:
        print(f"❌ Påminnelse har redan skickats (värde: {reminder_sent})")
        print()
        print("FIX: Skapa en ny händelse för att testa")
        return False

    # Kolla tidsfönsret
    event_time = datetime.strptime(f"{today} {event['time']}", '%Y-%m-%d %H:%M')
    event_time = event_time.replace(tzinfo=stockholm_tz)

    time_until = (event_time - now).total_seconds() / 60
    reminder_time = event_time - timedelta(minutes=15)

    print()
    print(f"⏰ Händelsen börjar: {event['time']}")
    print(f"🔔 Påminnelse ska skickas: {reminder_time.strftime('%H:%M')}")
    print(f"⏱️  Om {time_until:.0f} minuter")
    print()

    if time_until < 14:
        print("⚠️  Händelsen börjar om mindre än 14 minuter")
        print("    Påminnelsen borde redan ha skickats eller är precis på väg")
        print()
    elif time_until > 60:
        print("ℹ️  Händelsen är mer än 1 timme bort")
        print(f"   Påminnelsen kommer skickas vid {reminder_time.strftime('%H:%M')}")
        print()
    else:
        print("✅ Händelsen är i rätt tidsfönster för testning")
        print(f"   Påminnelsen kommer skickas vid ca {reminder_time.strftime('%H:%M')}")
        print()

    print("=" * 60)
    print("SLUTSATS:")
    print("=" * 60)

    if reminder in (1, True, '1') and reminder_sent in (0, False, None, '0'):
        print("✅ Händelsen kommer få påminnelse!")
        print(f"   Förvänta Telegram-meddelande vid ca {reminder_time.strftime('%H:%M')}")
        print()
        return True
    else:
        print("❌ Händelsen kommer INTE få påminnelse")
        print("   Skapa en ny händelse för att testa")
        print()
        return False

if __name__ == "__main__":
    try:
        success = check_event()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FEL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
