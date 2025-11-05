# Familjekalender

En modern familjekalender byggd med FastAPI, React och PostgreSQL. Designad för att vara gratis att köra på Railway.app med ntfy.sh för push-notifikationer.

## Funktioner

- Modern kalendervy liknande Google Calendar
- 5 användare med färgkodning: Albin (blå), Maria (röd), Olle (gul), Ellen (lila), Familj (grön)
- Skapa, redigera och ta bort händelser
- Påminnelser via ntfy.sh
- Heldag-händelser
- Responsiv design
- Gratis hosting på Railway.app

## Teknologier

### Backend
- FastAPI - Snabb Python web framework
- PostgreSQL - Databas (Railway tillhandahåller gratis)
- SQLAlchemy - ORM
- ntfy.sh - Push-notifikationer

### Frontend
- React - UI framework
- Vite - Build tool
- React Big Calendar - Kalenderkomponent
- date-fns - Datumhantering

## Installation

### Lokal utveckling

1. **Klona repository**
   ```bash
   git clone <repo-url>
   cd familjekalender
   ```

2. **Installera Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfigurera miljövariabler**
   ```bash
   cp .env.example .env
   # Redigera .env med dina inställningar
   ```

4. **Starta backend**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

5. **Initiera användare** (första gången)
   ```bash
   python backend/init_users.py
   ```

6. **Installera frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

7. **Starta frontend**
   ```bash
   npm run dev
   ```

Nu kan du öppna http://localhost:3000 i din webbläsare!

## Deployment på Railway.app

### Steg-för-steg guide

1. **Skapa Railway konto**
   - Gå till https://railway.app
   - Skapa konto (gratis, $5 kredit/månad)

2. **Pusha kod till GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Skapa nytt projekt på Railway**
   - Klicka på "New Project"
   - Välj "Deploy from GitHub repo"
   - Välj ditt repository

4. **Lägg till PostgreSQL databas**
   - I ditt Railway projekt, klicka "New"
   - Välj "Database" → "PostgreSQL"
   - Railway sätter automatiskt DATABASE_URL

5. **Konfigurera miljövariabler**
   - Gå till ditt projekt → Settings → Variables
   - Lägg till:
     ```
     NTFY_TOPIC=familjekalender-din-unika-id
     NTFY_URL=https://ntfy.sh
     ```

6. **Deploy backend**
   - Railway deployer automatiskt från GitHub
   - Vänta på att deployment är klar

7. **Initiera användare**
   - Efter första deployment, kör:
   ```bash
   railway run python backend/init_users.py
   ```

8. **Konfigurera frontend** (valfritt för produktion)
   - Bygg frontend lokalt:
     ```bash
     cd frontend
     VITE_API_URL=https://din-railway-url.up.railway.app npm run build
     ```
   - Eller använd en separat frontend hosting (Vercel/Netlify)

### Railway CLI

```bash
# Installera Railway CLI
npm i -g @railway/cli

# Login
railway login

# Länka projekt
railway link

# Kör kommando i Railway miljö
railway run python backend/init_users.py

# Visa logs
railway logs
```

## Användning

### Skapa en händelse
1. Klicka på en dag/tid i kalendern
2. Fyll i titel, välj person, tid, etc.
3. Aktivera påminnelse om önskat
4. Klicka "Spara"

### Redigera händelse
1. Klicka på en befintlig händelse
2. Ändra information
3. Klicka "Spara" eller "Ta bort"

### Notifikationer
Notifikationer skickas via ntfy.sh. För att ta emot dem:

1. **På mobilen:**
   - Installera ntfy app från App Store/Google Play
   - Prenumerera på topic: `familjekalender-din-unika-id`

2. **På datorn:**
   - Öppna https://ntfy.sh/familjekalender-din-unika-id
   - Aktivera notifikationer i webbläsaren

## API Endpoints

- `GET /api/users` - Hämta alla användare
- `GET /api/events` - Hämta alla händelser
- `POST /api/events` - Skapa ny händelse
- `PUT /api/events/{id}` - Uppdatera händelse
- `DELETE /api/events/{id}` - Ta bort händelse
- `POST /webhook` - Webhook endpoint
- `GET /health` - Health check

## Kostnad

Railway.app ger $5 gratis kredit per månad, vilket räcker för:
- PostgreSQL databas
- Backend hosting (FastAPI)
- ~500 timmar runtime/månad

ntfy.sh är helt gratis för publik användning.

**Total kostnad: 0 kr/månad** (under $5 kredit gränsen)

## Utveckling

### Projektstruktur
```
familjekalender/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # SQLAlchemy modeller
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # CRUD operationer
│   │   ├── database.py      # DB konfiguration
│   │   └── notifications.py # ntfy.sh integration
│   └── init_users.py        # Initiera användare
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── EventModal.jsx
│   │   │   └── EventModal.css
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── requirements.txt
├── Procfile
├── railway.toml
└── README.md
```

## Framtida förbättringar

- [ ] Återkommande händelser
- [ ] Delning av händelser mellan användare
- [ ] Export till iCal/Google Calendar
- [ ] Mörkt tema
- [ ] Mobilapp (React Native)
- [ ] Email-notifikationer

## Licens

MIT

## Support

För frågor eller problem, skapa ett issue på GitHub.
