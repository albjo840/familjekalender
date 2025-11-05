# Snabbstart Guide

## Lokal utveckling (5 minuter)

### 1. Installera dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Skapa lokal PostgreSQL databas
```bash
# Om du har Docker:
docker run --name familjekalender-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=familjekalender -p 5432:5432 -d postgres

# Eller installera PostgreSQL direkt:
# sudo apt install postgresql  (Linux)
# brew install postgresql      (Mac)
```

### 3. Initiera användare
```bash
python backend/init_users.py
```

### 4. Starta backend
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 5. Starta frontend (nytt terminalfönster)
```bash
cd frontend
npm run dev
```

### 6. Öppna i webbläsare
```
http://localhost:3000
```

## Railway Deployment (10 minuter)

### 1. Skapa Railway konto
- Gå till https://railway.app
- Logga in med GitHub
- Gratis $5/månad kredit

### 2. Pusha till GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 3. Deploy på Railway

#### A. Via Railway Dashboard
1. Gå till https://railway.app/new
2. Välj "Deploy from GitHub repo"
3. Välj `familjekalender` repository
4. Klicka "Add variables" → Lägg till:
   - `NTFY_TOPIC=familjekalender-[välj-unikt-namn]`
   - `NTFY_URL=https://ntfy.sh`
5. Klicka på "New" → "Database" → "PostgreSQL"
6. Vänta på deployment

#### B. Via Railway CLI
```bash
# Installera CLI
npm i -g @railway/cli

# Login
railway login

# Initiera projekt
railway init

# Lägg till PostgreSQL
railway add

# Sätt environment variables
railway variables set NTFY_TOPIC=familjekalender-[unikt-namn]
railway variables set NTFY_URL=https://ntfy.sh

# Deploy
railway up
```

### 4. Initiera användare på Railway
```bash
railway run python backend/init_users.py
```

### 5. Få din Railway URL
```bash
railway domain
```

### 6. Testa
Öppna din Railway URL i webbläsaren!

## Konfigurera notifikationer

### Mobil (iOS/Android)
1. Installera ntfy app
2. Lägg till prenumeration: `familjekalender-[ditt-unika-namn]`
3. Aktivera notifikationer

### Desktop
1. Öppna https://ntfy.sh/familjekalender-[ditt-unika-namn]
2. Klicka på klockan → "Enable notifications"

## Felsökning

### Backend startar inte
```bash
# Kolla att PostgreSQL körs
docker ps

# Kolla environment variables
echo $DATABASE_URL

# Se loggar
railway logs  # På Railway
```

### Frontend kan inte nå backend
```bash
# Kolla att VITE_API_URL är satt
cd frontend
cat .env

# Borde vara:
# VITE_API_URL=http://localhost:8000/api  (lokal)
# VITE_API_URL=https://din-app.up.railway.app/api  (produktion)
```

### Användare finns inte
```bash
# Kör init script igen
python backend/init_users.py

# Eller via Railway
railway run python backend/init_users.py
```

### Database error på Railway
```bash
# Kolla att PostgreSQL är tillagd
railway variables

# DATABASE_URL borde finnas automatiskt
```

## Nästa steg

- Lägg till händelser i kalendern
- Testa påminnelser
- Bjud in familjemedlemmar att prenumerera på ntfy topic
- Anpassa färger i `backend/init_users.py`

Lycka till! 🎉
