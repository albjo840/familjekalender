"""
Database Persistence Layer
===========================
Använder Supabase som primär molnbaserad databas med lokal SQLite som cache.
När Streamlit vaknar upp synkas data automatiskt från Supabase.

Fördelar:
- Persistent lagring i molnet (överlever Streamlit Cloud restart)
- Gratis PostgreSQL-databas
- Automatisk synkronisering
- Lokal cache för snabb åtkomst
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[WARNING] Supabase not installed. Run: pip install supabase")

class DatabasePersistence:
    """Hanterar databaspersistens med automatisk backup och återställning"""

    def __init__(self, db_path: str, backup_method: str = "supabase"):
        """
        Args:
            db_path: Sökväg till SQLite-databasen (används som lokal cache)
            backup_method: "json" eller "supabase"
        """
        self.db_path = db_path
        self.backup_method = backup_method
        self.backup_json_path = f"{db_path}.json"
        self.supabase_client: Optional[Client] = None

        # Initiera Supabase om tillgängligt
        if backup_method == "supabase" and SUPABASE_AVAILABLE:
            self._init_supabase()

    def _init_supabase(self) -> None:
        """Initierar Supabase-klienten med credentials från Streamlit secrets"""
        try:
            # Hämta credentials från Streamlit secrets
            supabase_url = st.secrets.get("SUPABASE_URL", "")
            supabase_key = st.secrets.get("SUPABASE_KEY", "")

            if not supabase_url or not supabase_key:
                print("[SUPABASE] Missing credentials in Streamlit secrets")
                print("[SUPABASE] Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml")
                self.backup_method = "json"  # Fallback till JSON
                return

            self.supabase_client = create_client(supabase_url, supabase_key)
            print("[SUPABASE] Successfully connected to Supabase")

        except Exception as e:
            print(f"[SUPABASE ERROR] Failed to initialize: {e}")
            self.backup_method = "json"  # Fallback till JSON

    def sync_to_supabase(self) -> bool:
        """Synkar alla händelser från lokal SQLite till Supabase"""
        if not self.supabase_client:
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Hämta alla händelser från lokal databas
            c.execute("""
                SELECT id, user, date, time, duration, title, description,
                       created_at, repeat_pattern, repeat_until, reminder
                FROM events
                ORDER BY date, time
            """)

            events = []
            for row in c.fetchall():
                events.append({
                    'local_id': row[0],
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

            if not events:
                print("[SUPABASE] No events to sync")
                return True

            # Rensa befintliga händelser i Supabase (full sync)
            self.supabase_client.table('events').delete().neq('id', 0).execute()

            # Lägg till alla händelser
            for event in events:
                self.supabase_client.table('events').insert(event).execute()

            print(f"[SUPABASE] Successfully synced {len(events)} events to cloud")
            return True

        except Exception as e:
            print(f"[SUPABASE SYNC ERROR] {e}")
            return False

    def restore_from_supabase(self) -> bool:
        """Återställer händelser från Supabase till lokal SQLite"""
        if not self.supabase_client:
            print("[SUPABASE] Client not initialized")
            return False

        try:
            # Hämta alla händelser från Supabase
            response = self.supabase_client.table('events').select('*').execute()
            events = response.data

            if not events:
                print("[SUPABASE] No events found in cloud database")
                return False

            print(f"[SUPABASE] Found {len(events)} events in cloud")

            # Återställ till lokal databas
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Kolla om lokal databas redan har händelser
            c.execute("SELECT COUNT(*) FROM events")
            existing_count = c.fetchone()[0]

            if existing_count > 0:
                print(f"[SUPABASE] Local database has {existing_count} events")
                # Rensa lokal databas för full sync
                c.execute("DELETE FROM events")
                print("[SUPABASE] Cleared local database for sync")

            # Återställ händelser från Supabase
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
                    event.get('repeat_pattern'),
                    event.get('repeat_until'),
                    event.get('reminder', 0)
                ))

            conn.commit()
            conn.close()

            print(f"[SUPABASE] Successfully restored {len(events)} events from cloud")
            return True

        except Exception as e:
            print(f"[SUPABASE RESTORE ERROR] {e}")
            return False

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

            print(f"[CHECK] Local database has {count} events")

            if count == 0:
                print("[CHECK] Local database is empty! Attempting restore...")

                # Försök återställa från Supabase först
                if self.backup_method == "supabase":
                    if self.restore_from_supabase():
                        return
                    print("[CHECK] Supabase restore failed, trying JSON...")

                # Fallback till JSON
                self.restore_from_json()

        except Exception as e:
            print(f"[CHECK ERROR] {e}")

    def auto_backup_on_change(self) -> None:
        """Körs automatiskt efter varje ändring"""
        if self.backup_method == "supabase":
            # Synka till både Supabase och JSON (JSON som extra backup)
            self.sync_to_supabase()
            self.backup_to_json()
        elif self.backup_method == "json":
            self.backup_to_json()


def create_persistent_db(db_path: str, use_supabase: bool = True) -> DatabasePersistence:
    """Factory function för att skapa en persistent databas

    Args:
        db_path: Sökväg till lokal SQLite-databas
        use_supabase: Använd Supabase för molnlagring (True) eller JSON backup (False)
    """
    backup_method = "supabase" if use_supabase else "json"
    persistence = DatabasePersistence(db_path, backup_method=backup_method)

    # Kontrollera och återställ vid start
    persistence.check_and_restore()

    return persistence
