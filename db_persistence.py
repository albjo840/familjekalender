"""
Database Persistence Layer
===========================
Hybrid lösning som använder både lokal SQLite och Google Sheets som backup.
När Streamlit vaknar upp synkas data automatiskt från Google Sheets.

Alternativ:
1. Google Sheets (gratis, pålitligt, osynligt)
2. JSON-fil som backup
3. Supabase (gratis PostgreSQL)
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabasePersistence:
    """Hanterar databaspersistens med automatisk backup och återställning"""

    def __init__(self, db_path: str, backup_method: str = "json"):
        """
        Args:
            db_path: Sökväg till SQLite-databasen
            backup_method: "json", "sheets", eller "supabase"
        """
        self.db_path = db_path
        self.backup_method = backup_method
        self.backup_json_path = f"{db_path}.json"

    def backup_to_json(self) -> bool:
        """Skapar JSON-backup av alla händelser"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Hämta alla händelser
            c.execute("""
                SELECT id, user, date, time, duration, title, description,
                       created_at, repeat_pattern, repeat_until, reminder
                FROM events
                ORDER BY date, time
            """)

            events = []
            for row in c.fetchall():
                events.append({
                    'id': row[0],
                    'user': row[1],
                    'date': row[2],
                    'time': row[3],
                    'duration': row[4],
                    'title': row[5],
                    'description': row[6],
                    'created_at': row[7],
                    'repeat_pattern': row[8],
                    'repeat_until': row[9],
                    'reminder': row[10]
                })

            conn.close()

            # Spara till JSON med timestamp
            backup_data = {
                'backup_time': datetime.now().isoformat(),
                'events': events
            }

            with open(self.backup_json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            print(f"[BACKUP] Saved {len(events)} events to {self.backup_json_path}")
            return True

        except Exception as e:
            print(f"[BACKUP ERROR] {e}")
            return False

    def restore_from_json(self) -> bool:
        """Återställer händelser från JSON-backup"""
        if not os.path.exists(self.backup_json_path):
            print(f"[RESTORE] No backup file found at {self.backup_json_path}")
            return False

        try:
            with open(self.backup_json_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            events = backup_data.get('events', [])
            backup_time = backup_data.get('backup_time', 'unknown')

            print(f"[RESTORE] Found backup from {backup_time} with {len(events)} events")

            # Återställ till databas
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Kolla om events redan finns
            c.execute("SELECT COUNT(*) FROM events")
            existing_count = c.fetchone()[0]

            if existing_count > 0:
                print(f"[RESTORE] Database already has {existing_count} events. Skipping restore.")
                conn.close()
                return False

            # Återställ händelser
            for event in events:
                c.execute("""
                    INSERT INTO events
                    (user, date, time, duration, title, description,
                     repeat_pattern, repeat_until, reminder)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event['user'],
                    event['date'],
                    event['time'],
                    event['duration'],
                    event['title'],
                    event['description'],
                    event['repeat_pattern'],
                    event['repeat_until'],
                    event.get('reminder', 0)
                ))

            conn.commit()
            conn.close()

            print(f"[RESTORE] Successfully restored {len(events)} events")
            return True

        except Exception as e:
            print(f"[RESTORE ERROR] {e}")
            return False

    def check_and_restore(self) -> None:
        """Kontrollerar om databasen är tom och återställer vid behov"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM events")
            count = c.fetchone()[0]
            conn.close()

            print(f"[CHECK] Database has {count} events")

            if count == 0:
                print("[CHECK] Database is empty! Attempting restore...")
                self.restore_from_json()

        except Exception as e:
            print(f"[CHECK ERROR] {e}")

    def auto_backup_on_change(self) -> None:
        """Körs automatiskt efter varje ändring"""
        if self.backup_method == "json":
            self.backup_to_json()


def create_persistent_db(db_path: str) -> DatabasePersistence:
    """Factory function för att skapa en persistent databas"""
    persistence = DatabasePersistence(db_path, backup_method="json")

    # Kontrollera och återställ vid start
    persistence.check_and_restore()

    return persistence
