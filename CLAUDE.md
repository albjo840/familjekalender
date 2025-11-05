# Claude Code Session - Familjekalender

## Projektöversikt

En modern familjekalender-applikation byggd med FastAPI (backend), React (frontend), PostgreSQL (Supabase), och deployad på Render.com + Vercel/Netlify.

**Skapad:** 2025-11-05
**Status:** Backend deployad och funktionell, Frontend deployment pågår

---

## Teknisk Stack

### Backend
- **Framework:** FastAPI 0.104.0
- **Databas:** PostgreSQL via Supabase (gratis tier)
- **ORM:** SQLAlchemy 2.0
- **Hosting:** Render.com (gratis tier)
- **API URL:** https://familjekalender.onrender.com

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite 5
- **Kalender:** React Big Calendar
- **Styling:** Custom CSS (Google Calendar-inspirerad)
- **Hosting:** TBD (Vercel eller Netlify)

### Notifikationer
- **Service:** ntfy.sh (gratis)
- **Topic:** `familjekalender-albin`
- **URL:** https://ntfy.sh/familjekalender-albin

---

## Projektstruktur

```
familjekalender/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app med endpoints
│   │   ├── models.py            # SQLAlchemy modeller (User, Event)
│   │   ├── schemas.py           # Pydantic schemas för validation
│   │   ├── crud.py              # CRUD operationer
│   │   ├── database.py          # Databas konfiguration
│   │   └── notifications.py    # ntfy.sh integration
│   └── init_users.py            # Script för att initiera användare
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Huvudkomponent med kalender
│   │   ├── App.css              # Huvudstyling
│   │   ├── components/
│   │   │   ├── EventModal.jsx  # Modal för skapa/redigera events
│   │   │   └── EventModal.css  # Modal styling
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global CSS + React Big Calendar styling
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── requirements.txt             # Python dependencies
├── Procfile                     # Render start command
├── railway.toml                 # Railway config (backup)
├── render.yaml                  # Render blueprint
├── .env.example                 # Example environment variables
├── .gitignore
├── README.md                    # Användardokumentation
├── QUICK_START.md               # Snabbstart guide
└── CLAUDE.md                    # Detta dokument

```

---

## Databas Schema

### Tabell: users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    color VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Användare (fördefinierade):**
- albin (blå #039BE5)
- maria (röd #D50000)
- olle (gul #F6BF26)
- ellen (lila #7986CB)
- familj (grön #33B679)

### Tabell: events
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    all_day BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id),
    reminder_enabled BOOLEAN DEFAULT FALSE,
    reminder_minutes INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Health Check
- `GET /health` - Returnerar {"status": "healthy"}

### Users
- `GET /api/users` - Hämta alla användare
- `GET /api/users/{user_id}` - Hämta specifik användare
- `POST /api/users` - Skapa ny användare (body: {name, color})

### Events
- `GET /api/events` - Hämta alla events (query params: start_date, end_date)
- `GET /api/events/{event_id}` - Hämta specifik event
- `POST /api/events` - Skapa ny event
- `PUT /api/events/{event_id}` - Uppdatera event
- `DELETE /api/events/{event_id}` - Ta bort event

### Webhook
- `POST /webhook` - Webhook endpoint för externa integrationer

---

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://postgres.xbhqtqjriiytkcnprteb:Sexfyra6@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
NTFY_TOPIC=familjekalender-albin
NTFY_URL=https://ntfy.sh
```

### Frontend (.env)
```bash
VITE_API_URL=https://familjekalender.onrender.com/api
```

### Render.com Environment Variables
Samma som backend .env ovan.

---

## Deployment

### Backend (Render.com)

**Status:** ✅ Deployad och Live
**URL:** https://familjekalender.onrender.com

**Deployment steg:**
1. GitHub repo kopplad till Render
2. Auto-deploy vid push till main branch
3. Environment variables satta i Render dashboard
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

**Första initiering:**
```bash
# Körs EN gång efter deployment för att skapa användare
python backend/init_users.py
```

### Frontend (Vercel/Netlify)

**Status:** ⏳ Pågår

**Deployment steg:**
1. `cd frontend && npm install`
2. `npm run build`
3. Deploy `dist/` mapp till Vercel/Netlify
4. Sätt VITE_API_URL environment variable

---

## Lokal Utveckling

### Backend
```bash
# Installera dependencies
pip install -r requirements.txt

# Sätt environment variables i .env
cp .env.example .env
# Redigera .env med dina värden

# Initiera användare (första gången)
python backend/init_users.py

# Starta server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend

# Installera dependencies
npm install

# Skapa .env för lokal utveckling
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Starta dev server
npm run dev
```

Öppna http://localhost:3000

---

## Notifikationer (ntfy.sh)

### Setup på Mobil
1. Installera ntfy app från App Store/Google Play
2. Lägg till subscription: `familjekalender-albin`
3. Aktivera notifikationer

### Setup på Desktop
1. Öppna https://ntfy.sh/familjekalender-albin
2. Klicka på klockan → "Enable notifications"

### Test Notifikation
```bash
curl -d "Test notifikation från familjekalender!" \
  https://ntfy.sh/familjekalender-albin
```

---

## Felsökning

### Backend startar inte på Render
- Kolla att DATABASE_URL är korrekt satt
- Verifiera att Supabase-projektet är aktivt
- Kolla logs i Render dashboard

### Database connection error
- Använd Supabase connection pooling URL (port 5432, inte 6543)
- Format: `postgresql://postgres.PROJECT:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:5432/postgres`

### Events endpoint ger Internal Server Error
- Kontrollera att tabellerna har rätt struktur (kör init_users.py igen)
- Radera gamla tabeller i Supabase Table Editor om de har fel struktur

### Frontend kan inte nå backend
- Kolla att VITE_API_URL pekar på rätt URL
- Verifiera CORS settings i backend (allow_origins)
- Testa backend direkt med curl först

---

## Kostnad & Limits

### Render.com (Backend)
- **Gratis tier:** 750 timmar/månad
- **Begränsning:** Sover efter 15 min inaktivitet, startar på ~30 sek
- **Kostnad:** $0/månad (under free tier)

### Supabase (Databas)
- **Gratis tier:** 500 MB databas, 2 GB dataöverföring
- **Begränsning:** Pausar efter 1 veckas inaktivitet (lätt att återaktivera)
- **Kostnad:** $0/månad

### Vercel/Netlify (Frontend)
- **Gratis tier:** 100 GB bandbredd/månad
- **Begränsning:** Inga för hobbyprojekt
- **Kostnad:** $0/månad

### ntfy.sh (Notifikationer)
- **Gratis tier:** Obegränsat för public topics
- **Kostnad:** $0/månad

**Total kostnad:** $0/månad ✅

---

## Nästa Steg

### Kortsiktigt (Session pågår)
- [ ] Installera frontend dependencies
- [ ] Konfigurera frontend för produktion
- [ ] Testa frontend lokalt
- [ ] Deploya frontend till Vercel/Netlify
- [ ] Konfigurera ntfy.sh på mobil
- [ ] Test end-to-end

### Långsiktigt (Framtida förbättringar)
- [ ] Återkommande händelser (daglig, veckovis, månadsvis)
- [ ] Delning av händelser mellan användare
- [ ] Export till iCal/Google Calendar
- [ ] Email-notifikationer (via SendGrid/Resend gratis tier)
- [ ] Mörkt tema
- [ ] Mobilapp (React Native)
- [ ] Attachments för händelser (bilder, dokument)
- [ ] Sökfunktion
- [ ] Filterering per användare
- [ ] Drag & drop i kalendern

---

## Git Workflow

### Branching Strategy
- `main` - Production branch (auto-deploy till Render)
- Feature branches för nya funktioner

### Commits
Alla commits gjorda av Claude Code följer formatet:
```
Type: Beskrivning

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Support & Dokumentation

### Projektdokumentation
- `README.md` - Användardokumentation
- `QUICK_START.md` - Snabbstart för utveckling
- `CLAUDE.md` - Detta dokument (teknisk referens)

### Externa länkar
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Big Calendar:** https://jquense.github.io/react-big-calendar/
- **Supabase Docs:** https://supabase.com/docs
- **Render Docs:** https://render.com/docs
- **ntfy.sh Docs:** https://docs.ntfy.sh

---

## Session Sammanfattning

### Vad vi gjort
1. ✅ Skapade helt ny familjekalender från scratch
2. ✅ Byggde FastAPI backend med PostgreSQL
3. ✅ Deployade till Render.com (gratis)
4. ✅ Konfigurerade Supabase databas
5. ✅ Skapade React frontend med modern UI
6. ✅ Integrerade ntfy.sh för notifikationer
7. ✅ Testade och verifierade alla API endpoints
8. ✅ Fixade databas-struktur problem
9. ⏳ Deployment av frontend pågår

### Lärdomar
- Railway.app har inte längre gratis tier → Bytte till Render.com
- Supabase connection pooling URL behövdes för Render
- Gamla databastabeller måste raderas vid schema-ändringar
- Init script behöver köras efter varje databas-reset

---

**Skapad med Claude Code 2025-11-05**
