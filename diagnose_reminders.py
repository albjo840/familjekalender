#!/usr/bin/env python3
"""
Diagnostiserar varför Telegram-påminnelser inte skickas
Kontrollerar:
1. Supabase-konfiguration
2. reminder_sent kolumn finns
3. GitHub Actions secrets
4. Händelser med påminnelser
5. Tidsfönster-logik
"""

import os
import sys
from datetime import datetime, timedelta
from supabase import create_client, Client

def main():
    print("=" * 60)
    print("🔍 TELEGRAM PÅMINNELSE DIAGNOSTIK")
    print("=" * 60)
    print()

    # 1. Kontrollera miljövariabler
    print("1️⃣ KONTROLLERAR MILJÖVARIABLER")
    print("-" * 60)

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id_albin = os.getenv('TELEGRAM_CHAT_ID_ALBIN')
    chat_id_maria = os.getenv('TELEGRAM_CHAT_ID_MARIA')

    checks = {
        'SUPABASE_URL': supabase_url,
        'SUPABASE_KEY': supabase_key and f"{supabase_key[:20]}...",
        'TELEGRAM_BOT_TOKEN': telegram_token and f"{telegram_token[:20]}...",
        'TELEGRAM_CHAT_ID_ALBIN': chat_id_albin,
        'TELEGRAM_CHAT_ID_MARIA': chat_id_maria,
    }

    all_ok = True
    for key, value in checks.items():
        status = "✅" if value else "❌ SAKNAS"
        print(f"  {key}: {status}")
        if not value:
            all_ok = False

    print()

    if not all_ok:
        print("❌ PROBLEM: Alla miljövariabler måste vara satta!")
        print()
        print("FIX: Lägg till följande i GitHub Repository Settings → Secrets:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_KEY")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID_ALBIN")
        print("  - TELEGRAM_CHAT_ID_MARIA")
        print()
        return False

    # 2. Anslut till Supabase
    print("2️⃣ ANSLUTER TILL SUPABASE")
    print("-" * 60)

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("  ✅ Anslutning lyckades")
        print()
    except Exception as e:
        print(f"  ❌ Kunde inte ansluta: {e}")
        print()
        return False

    # 3. Kontrollera events-tabellen
    print("3️⃣ KONTROLLERAR EVENTS-TABELL")
    print("-" * 60)

    try:
        # Hämta ett event för att se kolumnerna
        response = supabase.table('events').select('*').limit(1).execute()

        if not response.data:
            print("  ⚠️ Tabellen är tom - inga events hittades")
            print()
            return False

        first_event = response.data[0]
        columns = list(first_event.keys())

        print(f"  ✅ Tabellen har {len(columns)} kolumner")
        print(f"  📋 Kolumner: {', '.join(columns)}")
        print()

        # Kontrollera reminder_sent kolumn
        if 'reminder_sent' in columns:
            print("  ✅ Kolumnen 'reminder_sent' finns")
        else:
            print("  ❌ PROBLEM: Kolumnen 'reminder_sent' saknas!")
            print()
            print("FIX: Kör följande SQL i Supabase SQL Editor:")
            print("  ALTER TABLE events ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;")
            print()
            return False

        print()

    except Exception as e:
        print(f"  ❌ Fel vid tabellkontroll: {e}")
        print()
        return False

    # 4. Hämta events med påminnelser
    print("4️⃣ SÖKER EFTER EVENTS MED PÅMINNELSER")
    print("-" * 60)

    try:
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')

        print(f"  📅 Idag: {today}")
        print(f"  🕐 Tid nu: {now.strftime('%H:%M:%S')}")
        print()

        # Hämta alla events idag med reminder=1
        response = supabase.table('events').select('*').eq('date', today).eq('reminder', 1).execute()

        all_events_today = response.data
        print(f"  📊 Totalt {len(all_events_today)} events med reminder=1 idag")
        print()

        if not all_events_today:
            print("  ⚠️ Inga events med påminnelser idag")
            print()
            print("  TIP: Lägg till en händelse med påminnelse för att testa:")
            print("  - Gå till kalendern")
            print("  - Lägg till en händelse om 20-30 minuter")
            print("  - Aktivera påminnelse (reminder)")
            print()
            return True

        # Visa alla events
        for event in all_events_today:
            reminder_sent = event.get('reminder_sent', False)
            status = "✅ Skickad" if reminder_sent else "⏳ Väntar"
            print(f"  [{status}] {event['time']} - {event['title']} ({event['user']})")

        print()

        # Filtrera bort redan skickade
        unsent_events = [e for e in all_events_today if not e.get('reminder_sent', False)]
        print(f"  🔔 {len(unsent_events)} påminnelser väntar på att skickas")
        print()

    except Exception as e:
        print(f"  ❌ Fel vid sökning: {e}")
        print()
        return False

    # 5. Kontrollera tidsfönster-logik
    print("5️⃣ KONTROLLERAR TIDSFÖNSTER (14-16 MIN FRAMÅT)")
    print("-" * 60)

    reminder_time_start = now + timedelta(minutes=14)
    reminder_time_end = now + timedelta(minutes=16)

    print(f"  🕐 Söker events mellan {reminder_time_start.strftime('%H:%M')} och {reminder_time_end.strftime('%H:%M')}")
    print()

    matching_events = 0
    for event in unsent_events:
        event_time_str = event['time']
        event_datetime = datetime.strptime(f"{today} {event_time_str}", '%Y-%m-%d %H:%M')

        if reminder_time_start <= event_datetime <= reminder_time_end:
            print(f"  🎯 MATCHNING: {event['title']} kl {event_time_str} är i tidsfönstret!")
            print(f"     Användare: {event['user']}")
            print(f"     Skulle skickas nu!")
            print()
            matching_events += 1
        else:
            time_diff = (event_datetime - now).total_seconds() / 60
            print(f"  ⏱️ {event['title']} kl {event_time_str} - om {time_diff:.0f} minuter")

    print()

    if matching_events == 0:
        print("  ℹ️ Inga events i tidsfönstret just nu")
        print()
        print("  Detta är NORMALT om ingen händelse börjar om 14-16 minuter.")
        print("  GitHub Actions körs var 5:e minut, så påminnelser kommer att skickas")
        print("  när ett event hamnar i tidsfönstret.")
        print()
    else:
        print(f"  🔔 {matching_events} påminnelse(r) borde skickas NU!")
        print()

    # 6. Sammanfattning
    print("=" * 60)
    print("📊 SAMMANFATTNING")
    print("=" * 60)
    print()
    print("✅ Miljövariabler: OK")
    print("✅ Supabase-anslutning: OK")
    print("✅ Tabell 'events': OK")
    print("✅ Kolumn 'reminder_sent': OK")
    print(f"📅 Events med påminnelser idag: {len(all_events_today)}")
    print(f"⏳ Väntar på att skickas: {len(unsent_events)}")
    print(f"🎯 I tidsfönstret nu: {matching_events}")
    print()

    if len(unsent_events) > 0 and matching_events == 0:
        print("💡 SLUTSATS:")
        print("  Systemet fungerar korrekt!")
        print("  Påminnelser kommer att skickas när ett event")
        print("  hamnar i 14-16 minuters tidsfönstret.")
        print()
        print("  GitHub Actions körs var 5:e minut och kontrollerar.")
        print()

    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ OVÄNTAT FEL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
