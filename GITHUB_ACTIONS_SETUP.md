# GitHub Actions Setup - Automatiska Påminnelser

## Översikt
GitHub Actions kör `reminder_service.py` varje 5:e minut för att skicka Telegram-påminnelser, **även när ingen använder appen**.

## Setup-instruktioner

### 1. Pusha koden till GitHub

```bash
git add .
git commit -m "Add GitHub Actions reminder service"
git push origin main
```

### 2. Lägg till Secrets i GitHub Repository

Gå till ditt GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Lägg till följande secrets:

| Secret Name | Värde | Hämta från |
|------------|-------|-----------|
| `SUPABASE_URL` | `https://***REMOVED***` | `.streamlit/secrets.toml` |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | `.streamlit/secrets.toml` |
| `TELEGRAM_BOT_TOKEN` | `8405404185:AAHGajxTL...` | `.streamlit/secrets.toml` |
| `TELEGRAM_CHAT_ID_ALBIN` | `***REMOVED***` | `.streamlit/secrets.toml` |
| `TELEGRAM_CHAT_ID_MARIA` | `***REMOVED***` | `.streamlit/secrets.toml` |
| `TELEGRAM_CHAT_ID_OLLE` | (frivilligt) | Om ni vill att Olle får påminnelser |
| `TELEGRAM_CHAT_ID_ELLEN` | (frivilligt) | Om ni vill att Ellen får påminnelser |
| `TELEGRAM_CHAT_ID_FAMILJ` | (frivilligt) | För gemensamma påminnelser |

### 3. Aktivera GitHub Actions

1. Gå till **Actions** fliken i ditt repository
2. Om det är första gången: Klicka "I understand my workflows, go ahead and enable them"
3. Du bör se "Reminder Service" workflow listad

### 4. Testa manuellt (valfritt)

1. Gå till **Actions** → **Reminder Service**
2. Klicka "Run workflow" → "Run workflow"
3. Vänta 30 sekunder och kolla loggen för att se att det fungerar

### 5. Skapa ett test-event

För att verifiera att systemet fungerar:

1. Öppna familjekalendern
2. Skapa ett event **16 minuter framåt i tiden**
3. Bocka i "🔔 Påminnelse 15 min innan"
4. Spara eventet
5. Vänta 1-2 minuter tills GitHub Actions nästa körning
6. Du bör få en Telegram-påminnelse!

## Hur det fungerar

### Tidsschema
- GitHub Actions kör **varje 5:e minut** (GitHub's minsta intervall)
- Skriptet letar efter events **14-16 minuter framåt i tiden**
- Detta ger ett 2-minuters fönster för påminnelser

### Flöde
```
GitHub Actions (varje 5 min)
    ↓
reminder_service.py körs
    ↓
Ansluter till Supabase
    ↓
Hämtar dagens events med reminder=1 och reminder_sent=0
    ↓
Filtrerar events som är 14-16 min bort
    ↓
Skickar Telegram-meddelande
    ↓
Uppdaterar reminder_sent=1 i Supabase
```

### Fördelar
- ✅ **Fungerar 24/7** - Även när ingen använder appen
- ✅ **100% gratis** - GitHub Actions är gratis för publika repos
- ✅ **Pålitligt** - GitHub's infrastruktur
- ✅ **Molnbaserat** - Ingen server behövs
- ✅ **Oberoende** - Fungerar även om Streamlit Cloud är nere

### Begränsningar
- ⏱️ Minsta intervall är 5 minuter (GitHub Actions begränsning)
- 🕐 Cron körs på UTC-tid (behöver justera för svensk tid om nödvändigt)
- 📊 Gratis tier: 2000 minuter/månad (räcker gott för detta)

## Övervaka systemet

### Se loggar
1. Gå till **Actions** → **Reminder Service**
2. Klicka på senaste körningen
3. Klicka på "send-reminders" jobbet
4. Se detaljerade loggar

### Exempel på logg vid lyckad påminnelse:
```
[2025-10-19 18:17:53] Checking for reminders...
[SUPABASE] Connected successfully
[TIME] Looking for events between 18:31 and 18:33
[EVENTS] Found 1 events with unsent reminders today
[MATCH] Event 'Fotbollsträning' for Ellen at 18:32 is in reminder window
[SENT] Reminder sent to Ellen
[UPDATE] Marked event 123 as reminder_sent=true
[SUMMARY] Sent 1 reminder(s)
```

## Felsökning

### Påminnelser skickas inte
1. Kolla att alla Secrets är korrekt inställda i GitHub
2. Kolla att eventet har `reminder=1` i Supabase
3. Kolla att eventet är 14-16 minuter bort
4. Kolla Actions-loggen för felmeddelanden

### "Missing required environment variables"
- Secrets är inte konfigurerade i GitHub repository settings

### "No events with unsent reminders today"
- Inga events idag med påminnelse aktiverad
- Eller alla påminnelser redan skickade (reminder_sent=1)

### Telegram-meddelande skickas inte
- Kolla att chat ID är korrekt
- Verifiera att bot token är giltig
- Testa skicka manuellt via Telegram API

## Avancerat: Justera frekvens

Om du vill köra oftare än varje 5 minut (kräver betald GitHub plan):

```yaml
# .github/workflows/reminder-service.yml
on:
  schedule:
    - cron: '* * * * *'  # Varje minut (kräver GitHub Teams/Enterprise)
```

För free tier är 5 minuter det minsta intervallet.

## Stänga av automatiska påminnelser

Om du vill pausa GitHub Actions:

1. Gå till **Actions** → **Reminder Service**
2. Klicka "..." → "Disable workflow"

Eller ta bort filen `.github/workflows/reminder-service.yml`
