# Supabase Setup för Familjekalender

## Varför Supabase?

Supabase ger dig en gratis PostgreSQL-databas i molnet som överlever när Streamlit Cloud startar om. Dina händelser försvinner aldrig mer!

## Steg 1: Skapa Supabase-konto (5 min)

1. Gå till https://supabase.com
2. Klicka på "Start your project"
3. Logga in med GitHub (rekommenderat) eller email
4. Det är **100% gratis** - ingen betalning krävs

## Steg 2: Skapa nytt projekt (2 min)

1. Klicka på "New Project"
2. Fyll i:
   - **Name**: `familjekalender` (eller valfritt namn)
   - **Database Password**: Välj ett starkt lösenord (spara det!)
   - **Region**: Välj `North Europe (Stockholm)` för bästa prestanda
3. Klicka på "Create new project"
4. Vänta 1-2 minuter medan projektet skapas

## Steg 3: Skapa events-tabell (3 min)

1. Klicka på **"Table Editor"** i vänster sidopanel
2. Klicka på **"Create a new table"**
3. Konfigurera tabellen:
   - **Name**: `events`
   - **Description**: "Familjekalender händelser"
4. Lägg till kolumner (klicka "Add column" för varje):

| Column Name      | Type      | Default Value | Extra                    |
|-----------------|-----------|---------------|--------------------------|
| id              | int8      | -             | Primary, Auto-increment  |
| local_id        | int8      | -             | -                        |
| user            | text      | -             | -                        |
| date            | text      | -             | -                        |
| time            | text      | -             | -                        |
| duration        | float8    | 1             | -                        |
| title           | text      | -             | -                        |
| description     | text      | -             | -                        |
| created_at      | timestamp | now()         | -                        |
| repeat_pattern  | text      | NULL          | Nullable                 |
| repeat_until    | text      | NULL          | Nullable                 |
| reminder        | int2      | 0             | -                        |

5. Klicka på **"Save"**

## Steg 4: Hämta API-nycklar (2 min)

1. Klicka på **"Settings"** (kugghjulsikon) i vänster sidopanel
2. Klicka på **"API"**
3. Under **"Project URL"** - kopiera URL:en (ex: `https://xxxxxxxxxxxxx.supabase.co`)
4. Under **"Project API keys"** - kopiera **"anon/public"** nyckeln
5. Spara båda dessa - du behöver dem strax!

## Steg 5: Uppdatera Streamlit secrets (3 min)

### För lokal utveckling:

1. Öppna `.streamlit/secrets.toml` i projektet
2. Lägg till dina Supabase-nycklar:

```toml
# Befintliga secrets
HUGGINGFACE_API_KEY = "hf_xxxxxxxxxxxxx"

# Nya Supabase secrets
SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

3. Spara filen

### För Streamlit Cloud:

1. Gå till https://share.streamlit.io
2. Hitta din familjekalender-app
3. Klicka på "⋮" (tre prickar) → "Settings"
4. Klicka på "Secrets"
5. Lägg till:

```toml
HUGGINGFACE_API_KEY = "hf_xxxxxxxxxxxxx"
SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

6. Klicka "Save"

## Steg 6: Migrera befintliga händelser (valfritt)

Om du har befintliga händelser i `familjekalender.db.json`:

1. Starta appen lokalt: `streamlit run app.py`
2. Dina händelser kommer automatiskt synkas till Supabase!
3. Kolla i Supabase Table Editor - du bör se dina händelser där

## Steg 7: Testa att det fungerar

1. **Lägg till en händelse** i kalendern
2. **Stäng appen** helt (Ctrl+C)
3. **Ta bort `familjekalender.db`** (för att simulera restart):
   ```bash
   rm familjekalender.db
   ```
4. **Starta appen igen**: `streamlit run app.py`
5. **Dina händelser finns kvar!** ✅

## Felsökning

### Problem: "SUPABASE_URL not found"
- Kolla att `.streamlit/secrets.toml` finns och innehåller rätt nycklar
- På Streamlit Cloud: Kolla att du lagt till secrets i Settings

### Problem: "Failed to connect to Supabase"
- Kolla att URL:en och API-nyckeln är rätt kopierade (inga extra mellanslag)
- Testa URL:en i webbläsaren - den ska visa en JSON-respons

### Problem: "Table 'events' does not exist"
- Gå till Supabase Table Editor och skapa tabellen enligt steg 3

### Problem: Händelser syns inte efter restart
- Kolla Supabase Table Editor - finns händelserna där?
- Kolla terminalloggar för "[SUPABASE]" meddelanden

## Gratis tier limits (mer än tillräckligt!)

- **Database size**: 500 MB
- **Bandwidth**: 5 GB/månad
- **API requests**: Unlimited
- **Rows**: Unlimited

För en familjekalender kommer du **aldrig nå gränserna**.

## Backup och säkerhet

- Händelser sparas både i Supabase (molnet) och `familjekalender.db.json` (lokal backup)
- Supabase gör automatiska backups varje dag
- Du kan exportera data när som helst via Table Editor

## Nästa steg

När allt fungerar:
1. ✅ Push till GitHub
2. ✅ Deploy på Streamlit Cloud
3. ✅ Lägg till Supabase secrets i Streamlit Cloud
4. ✅ Njut av en kalender som aldrig glömmer dina händelser!

## Support

- Supabase docs: https://supabase.com/docs
- Streamlit secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
