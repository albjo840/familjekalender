"""
Script för att initiera användare med färger
Kör detta en gång efter deployment för att skapa alla användare
"""
from dotenv import load_dotenv
load_dotenv()  # Ladda .env-filen

from app import models  # Importera models först så de registreras
from app.database import SessionLocal, engine, Base
from app import crud, schemas

def init_users():
    # Skapa alla tabeller först
    print("Skapar databas-tabeller...")
    models.Base.metadata.create_all(bind=engine)
    print("Tabeller skapade!")

    db = SessionLocal()

    # Definiera användare med Google Calendar-liknande färger
    users = [
        {"name": "albin", "color": "#039BE5"},   # Ljusblå
        {"name": "maria", "color": "#D50000"},   # Röd
        {"name": "olle", "color": "#F6BF26"},    # Gul
        {"name": "ellen", "color": "#7986CB"},   # Lila
        {"name": "familj", "color": "#33B679"},  # Grön
    ]

    for user_data in users:
        # Kolla om användaren redan finns
        existing_user = crud.get_user_by_name(db, name=user_data["name"])
        if not existing_user:
            user = schemas.UserCreate(**user_data)
            crud.create_user(db=db, user=user)
            print(f"Skapade användare: {user_data['name']} med färg {user_data['color']}")
        else:
            print(f"Användare {user_data['name']} finns redan")

    db.close()
    print("Användare initierade!")

if __name__ == "__main__":
    init_users()
