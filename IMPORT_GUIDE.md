# Guide: Importera befintliga händelser till Supabase

## Översikt

Du har **4 händelser** i din lokala databas som behöver flyttas till Supabase:

1. **Olle - Blåskul** (Musiklektion, torsdagar)
2. **Olle - Handbollsträning** (Onsdagar)
3. **Olle - Innebandy** (Söndagar)
4. **Ellen - Fotbollsträning** (Måndagar)

## Steg-för-steg import

### 1. Förberedelser (om du inte gjort det än)

Följ `SUPABASE_SETUP.md` för att:
- ✅ Skapa Supabase-konto
- ✅ Skapa projekt
- ✅ Skapa `events` tabell
- ✅ Lägg till SUPABASE_URL och SUPABASE_KEY i `.streamlit/secrets.toml`

### 2. Installera dependencies

```bash
cd /home/albin/familjekalender
pip install supabase
```

### 3. Kör import-skriptet

```bash
python import_to_supabase.py
```

**Vad händer:**
- Skriptet läser `familjekalender.db.json`
- Ansluter till din Supabase-databas
- Importerar alla 4 händelser
- Verifierar att importen lyckades

### 4. Exempel på output

```
============================================================
📦 Supabase Import Script
============================================================
✅ Hittade 4 händelser i lokal backup

Händelser att importera:
  - Olle: Blåskul (2025-10-06)
  - Olle: Handbollsträning (2025-10-06)
  - Olle: Innebandy (2025-10-13)
  - Ellen: Fotbollsträning (2025-11-03)

============================================================
✅ Ansluten till Supabase: https://xxxxxxxxxxxxx.supabase...

============================================================
📤 Börjar importera 4 händelser...
  [1/4] ✅ Olle: Blåskul (2025-10-06 16:50)
  [2/4] ✅ Olle: Handbollsträning (2025-10-06 17:00)
  [3/4] ✅ Olle: Innebandy (2025-10-13 09:00)
  [4/4] ✅ Ellen: Fotbollsträning (2025-11-03 17:00)

============================================================
✅ Import klar!
   - Lyckade: 4
   - Misslyckade: 0
============================================================

🔍 Verifiering: 4 händelser finns nu i Supabase

Första händelsen i databasen:
  - ID: 1
  - Användare: Olle
  - Titel: Blåskul
  - Datum: 2025-10-06 16:50

✅ Klart! Gå till Supabase Table Editor för att se dina händelser:
   https://app.supabase.com/project/_/editor

💡 Nästa steg: Kör 'streamlit run app.py' för att testa!
```

### 5. Verifiera i Supabase

1. Gå till https://app.supabase.com
2. Öppna ditt projekt
3. Klicka på **"Table Editor"** → **"events"**
4. Du ska se alla 4 händelser listade! ✅

### 6. Testa i appen

```bash
streamlit run app.py
```

Dina händelser ska nu visas i kalendern! 🎉

## Alternativ metod: Manuell SQL-import

Om skriptet inte fungerar kan du importera manuellt via SQL:

1. Gå till Supabase **SQL Editor**
2. Klistra in följande SQL:

```sql
INSERT INTO events (local_id, user, date, time, duration, title, description, created_at, repeat_pattern, repeat_until, reminder)
VALUES
(37, 'Olle', '2025-10-06', '16:50', 1, 'Blåskul', 'Musiklektion', '2025-10-09 19:53:35', 'tor', '2026-01-04', 0),
(35, 'Olle', '2025-10-06', '17:00', 1, 'Handbollsträning', 'Träning med laget', '2025-10-09 19:53:35', 'ons', '2026-01-04', 0),
(40, 'Olle', '2025-10-13', '09:00', 1.5, 'Innebandy', 'Innebandyträning', '2025-10-13 19:04:54', 'sön', '2026-01-04', 0),
(38, 'Ellen', '2025-11-03', '17:00', 1, 'Fotbollsträning', 'Träning', '2025-10-09 19:54:23', 'mån', '2026-02-01', 0);
```

3. Klicka **"Run"**
4. Du ska se: "Success. 4 rows affected"

## Felsökning

### Problem: "SUPABASE_URL saknas"
**Lösning:**
```bash
# Kolla att filen finns
cat .streamlit/secrets.toml

# Den ska innehålla:
SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

### Problem: "Table 'events' does not exist"
**Lösning:**
- Gå till Supabase Table Editor
- Skapa `events` tabell enligt SUPABASE_SETUP.md

### Problem: "Permission denied"
**Lösning:**
- Kolla att du använder **anon/public key** (inte service_role key)
- Kontrollera att tabellen har rätt RLS-policies (Row Level Security)
  - Gå till Authentication → Policies
  - Aktivera "Enable RLS" men lägg till en policy som tillåter alla operationer för utveckling

### Problem: Dubbletter efter import
**Lösning:**
Om du kört importen flera gånger:
```sql
-- Radera alla händelser
DELETE FROM events;

-- Kör importen igen
```

## Efter lyckad import

✅ **Dina händelser är nu säkra i molnet!**

- Händelser synkas automatiskt vid varje ändring
- Streamlit Cloud restart = inga problem
- Du kan ta bort lokal databas när som helst - händelser återställs automatiskt

## Nästa steg

1. ✅ Importera händelser (du är här!)
2. ✅ Testa att appen fungerar lokalt
3. ✅ Commit och push till GitHub
4. ✅ Deploy till Streamlit Cloud
5. ✅ Lägg till Supabase secrets i Streamlit Cloud
6. ✅ Njut av en kalender som aldrig glömmer! 🎉
