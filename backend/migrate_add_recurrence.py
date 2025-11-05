"""
Migration script to add recurrence columns to events table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

load_dotenv()

def migrate():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("Adding recurrence columns to events table...")

        # Add recurrence_type column
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_type VARCHAR DEFAULT 'none'
            """))
            print("✓ Added recurrence_type column")
        except Exception as e:
            print(f"Note: recurrence_type column might already exist: {e}")

        # Add recurrence_interval column
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_interval INTEGER DEFAULT 1
            """))
            print("✓ Added recurrence_interval column")
        except Exception as e:
            print(f"Note: recurrence_interval column might already exist: {e}")

        # Add recurrence_end_date column
        try:
            conn.execute(text("""
                ALTER TABLE events
                ADD COLUMN IF NOT EXISTS recurrence_end_date TIMESTAMP
            """))
            print("✓ Added recurrence_end_date column")
        except Exception as e:
            print(f"Note: recurrence_end_date column might already exist: {e}")

        conn.commit()
        print("\n✓ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
