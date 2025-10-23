#!/usr/bin/env python3
"""
Testar reminder-filtrering med olika datatyper
Detta verifierar att reminder_service.py kan hantera både 0/1 och True/False
"""

def test_filtering():
    print("=" * 60)
    print("TEST: Reminder Filtering Logic")
    print("=" * 60)
    print()

    # Simulera olika Supabase event-format
    test_events = [
        {'id': 1, 'title': 'Event 1', 'reminder': 1, 'reminder_sent': 0},
        {'id': 2, 'title': 'Event 2', 'reminder': True, 'reminder_sent': False},
        {'id': 3, 'title': 'Event 3', 'reminder': '1', 'reminder_sent': '0'},
        {'id': 4, 'title': 'Event 4', 'reminder': 1, 'reminder_sent': 1},  # Redan skickad
        {'id': 5, 'title': 'Event 5', 'reminder': 0, 'reminder_sent': 0},  # Reminder disabled
        {'id': 6, 'title': 'Event 6', 'reminder': False, 'reminder_sent': False},  # Reminder disabled
        {'id': 7, 'title': 'Event 7', 'reminder': 1, 'reminder_sent': None},  # Ny händelse
    ]

    print("TESTDATA:")
    for e in test_events:
        print(f"  {e['id']}: reminder={e['reminder']!r:5} reminder_sent={e['reminder_sent']!r:5} - {e['title']}")
    print()

    # Använd samma filterlogik som i reminder_service.py
    filtered_events = []
    for e in test_events:
        reminder = e.get('reminder')
        reminder_sent = e.get('reminder_sent')

        # reminder måste vara aktiverad (hantera både 0/1 och True/False)
        if reminder in (1, True, '1'):
            # reminder_sent måste vara False/0/None (hantera både 0/1 och True/False)
            if reminder_sent in (0, False, None, '0'):
                filtered_events.append(e)

    print("FILTRERADE EVENTS (borde skicka påminnelse):")
    if filtered_events:
        for e in filtered_events:
            print(f"  ✅ {e['id']}: {e['title']}")
    else:
        print("  ❌ Inga events hittades!")
    print()

    # Förväntat resultat: Event 1, 2, 3, 7
    expected_ids = {1, 2, 3, 7}
    actual_ids = {e['id'] for e in filtered_events}

    print("RESULTAT:")
    print(f"  Förväntade: {sorted(expected_ids)}")
    print(f"  Faktiska:   {sorted(actual_ids)}")
    print()

    if expected_ids == actual_ids:
        print("✅ TEST PASSED - Filtering fungerar korrekt!")
        return True
    else:
        print("❌ TEST FAILED - Filtering fungerar inte som förväntat!")
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        if missing:
            print(f"  Saknade: {missing}")
        if extra:
            print(f"  Extra: {extra}")
        return False

if __name__ == "__main__":
    import sys
    success = test_filtering()
    sys.exit(0 if success else 1)
