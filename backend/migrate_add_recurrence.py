"""
Migration script för att lägga till recurrence-kolumner till events-tabellen
Körs en gång för att uppdatera databas-schemat
"""
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.database import engine

def migrate():
    print("Startar migration för att lägga till recurrence-kolumner...")

    with engine.connect() as conn:
        # Lägg till recurrence_type kolumn
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_type VARCHAR DEFAULT 'none'
            """))
            conn.commit()
            print("✓ Lade till recurrence_type kolumn")
        except Exception as e:
            print(f"recurrence_type: {e}")

        # Lägg till recurrence_interval kolumn
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1
            """))
            conn.commit()
            print("✓ Lade till recurrence_interval kolumn")
        except Exception as e:
            print(f"recurrence_interval: {e}")

        # Lägg till recurrence_end_date kolumn
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP
            """))
            conn.commit()
            print("✓ Lade till recurrence_end_date kolumn")
        except Exception as e:
            print(f"recurrence_end_date: {e}")

    print("\nMigration klar! Databas-schemat är uppdaterat.")

if __name__ == "__main__":
    migrate()
