# Testa Persistent Lagring

## Snabbtest (Lokal utveckling)

### Steg 1: Förbered testmiljö
```bash
cd /home/albin/familjekalender

# Installera Supabase
pip install supabase

# Kontrollera att koden är uppdaterad
cat requirements.txt  # Ska innehålla "supabase>=2.0.0"
```

### Steg 2: Konfigurera Supabase (först)

Följ `SUPABASE_SETUP.md` för att:
1. Skapa Supabase-konto
2. Skapa projekt och `events` tabell
3. Lägg till credentials i `.streamlit/secrets.toml`

### Steg 3: Testa att det fungerar

```bash
# 1. Starta appen
streamlit run app.py

# 2. Lägg till några händelser via UI:t

# 3. Kolla att synkning fungerar
# Du ska se meddelanden i terminalen:
# [SUPABASE] Successfully connected to Supabase
# [SUPABASE] Successfully synced X events to cloud

# 4. Verifiera i Supabase
# Gå till Supabase Table Editor -> events
# Du ska se dina händelser där!
```

### Steg 4: Simulera Streamlit Cloud restart

```bash
# 1. Stoppa appen (Ctrl+C)

# 2. Ta bort lokal databas (simulerar restart)
rm familjekalender.db

# 3. Starta appen igen
streamlit run app.py

# 4. Du ska se:
# [CHECK] Local database has 0 events
# [CHECK] Local database is empty! Attempting restore...
# [SUPABASE] Found X events in cloud
# [SUPABASE] Successfully restored X events from cloud

# 5. Dina händelser finns kvar! ✅
```

## Test utan Supabase (Fallback)

Om Supabase inte är konfigurerat:

```bash
# Appen faller tillbaka på JSON-backup
# Du ska se:
# [SUPABASE] Missing credentials in Streamlit secrets
# [RESTORE] Found backup from [timestamp] with X events
```

## Streamlit Cloud Test

### Efter deployment:

1. **Lägg till händelser** via deployed app
2. **Vänta 15 minuter** (eller längre) tills Streamlit Cloud går i viloläge
3. **Besök appen igen** - händelserna finns kvar! ✅

### Felsökning i Streamlit Cloud:

1. Gå till "Manage app" → "Logs"
2. Sök efter "[SUPABASE]" meddelanden:
   - ✅ "Successfully connected to Supabase"
   - ✅ "Successfully synced X events to cloud"
   - ❌ "Missing credentials" → Lägg till secrets
   - ❌ "Failed to connect" → Kolla credentials

## Verifiering

### Kolla Supabase Table Editor:
1. Logga in på https://supabase.com
2. Öppna ditt projekt
3. Gå till "Table Editor" → "events"
4. Du ska se alla dina händelser listade

### Kolla lokal JSON backup:
```bash
cat familjekalender.db.json
# Ska visa alla händelser i JSON-format
```

## Vanliga problem

### Problem: Händelser försvinner fortfarande
**Lösning:**
- Kolla Streamlit Cloud secrets (Settings → Secrets)
- Verifiera att SUPABASE_URL och SUPABASE_KEY är korrekt inlagda
- Kolla Streamlit Cloud logs för felmeddelanden

### Problem: "Table 'events' does not exist"
**Lösning:**
- Gå till Supabase Table Editor
- Skapa `events` tabell enligt SUPABASE_SETUP.md

### Problem: Dubbletter av händelser
**Lösning:**
- Detta händer vid första synkningen om både lokal och cloud har data
- Radera dubbletter i Supabase Table Editor
- Eller: DELETE FROM events i SQL Editor och synka igen

## Framgång! ✅

Om du ser följande är allting korrekt:

1. ✅ Terminal visar: "[SUPABASE] Successfully connected to Supabase"
2. ✅ Händelser syns i Supabase Table Editor
3. ✅ Efter `rm familjekalender.db` och omstart - händelser finns kvar
4. ✅ Streamlit Cloud restart bevarar händelserna

**Nu kan du använda familjekalendern utan oro - dina händelser är säkra i molnet!**
