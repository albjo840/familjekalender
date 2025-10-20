# Familjekalender

En modern, AI-driven familjekalender byggd med Streamlit för att hantera och dela händelser mellan familjemedlemmar.

## Beskrivning

Detta projekt är en fullständig familjekalenderapp med veckovisning, AI-assistent för bokningar och frågor, samt stöd för återkommande händelser. Appen är installationsbar som PWA (Progressive Web App) och optimerad för både desktop och mobil.

## Kom igång

### Installation

```bash
# Klona repository
git clone https://github.com/albjo840/familjekalender.git
cd familjekalender

# Installera beroenden
pip install -r requirements.txt

# Kör appen
streamlit run app.py
```

### Konfiguration (REKOMMENDERAT)

#### 1. Supabase Database (VIKTIGT - för persistent lagring)

**OBS: Detta löser problemet med att händelser försvinner när appen startar om!**

1. Skapa ett gratis konto på Supabase: https://supabase.com
2. Skapa ett nytt projekt och en `events` tabell
3. Lägg till Supabase credentials i `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://xxxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

**📖 Fullständig guide**: Se `SUPABASE_SETUP.md` för steg-för-steg instruktioner!

#### 2. AI-assistent (Groq)

1. Skapa ett gratis konto på Groq: https://console.groq.com
2. Skapa en API-nyckel från API Keys-sektionen
3. Lägg till din Groq API-nyckel i `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxx"
```

Modell som används: **Llama 3.3 70B Versatile** (100% gratis, extremt snabb via Groq API)

## Funktioner

### Kalender
- **Veckovisning**: Måndag-Söndag, 7:00-22:00
- **5 användare**: Albin, Maria, Olle, Ellen, Familj
- **Färgkodning**: Unik gradient för varje användare
- **Varaktighet**: Händelser kan vara 1-12 timmar långa
- **Återkommande händelser**: Veckovisa upprepningar med slutdatum

### AI-Assistent
- **Sticky chat-bar**: Röstknapp + textinput följer med längst ner (chatbot-stil)
- **Röstinmatning**: Web Speech API med svensk språkstöd
- **Smart frågehantering**:
  - "Vad gör Albin 17e oktober?" → Filtrerar på användare och datum
  - "Vad finns bokat nästa vecka?" → Visar alla händelser
  - "När är Maria ledig på fredag?" → Analyserar lediga tider
- **Bokningar via naturligt språk**:
  - "Boka lunch för Maria imorgon kl 12"
  - "Lägg till tandläkare för Albin på fredag 14:00"
  - "Skapa familjemiddag på lördag 18:00 i 2 timmar"
- **Qwen 2.5 72B**: 9x kraftfullare än tidigare modell

### Påminnelser (Telegram)
- **Push-notiser till telefonen**: 15 minuter innan händelser
- **100% gratis**: Via Telegram Bot API + GitHub Actions
- **Fungerar överallt**: iOS, Android, Desktop
- **Pålitligt 24/7**: GitHub Actions kör automatiskt varje 5:e minut
- **Oberoende**: Fungerar även när ingen använder appen
- **Multi-användare**: Stöd för hela familjen

**Setup-krav:**
1. Lägg till kolumn i Supabase: `ALTER TABLE events ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;`
2. Konfigurera GitHub Secrets (SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_*)
3. Telegram-bot: @familjekalender_bot
4. För att undvika GitHub mail-spam: Stäng av Actions-notiser i https://github.com/settings/notifications

### Händelsehantering
- **Lägg till händelser**: Via formulär eller AI-assistent
- **Redigera händelser**: Ändra tid, varaktighet, beskrivning
- **Ta bort händelser**: Enskilda eller alla förekomster av återkommande händelser
- **Veckonavigation**: Enkel navigering mellan veckor
- **Persistent lagring**: Supabase molndatabas - händelser försvinner aldrig!
  - Automatisk synkronisering till molnet
  - Fungerar även när Streamlit Cloud startar om
  - Lokal JSON backup som extra säkerhet

### Design
- **Apple-liknande UI**: Modern design med gradienter och glasmorfism
- **Mobil-responsiv**: Optimerad för alla skärmstorlekar
- **PWA-stöd**: Installationsbar på mobil och desktop
- **Animationer**: Smooth transitions och hover-effekter

## Teknisk stack

### Frontend
- **Streamlit**: Huvudramverk för UI
- **Custom CSS**: Apple-inspirerad design med glasmorfism
- **Web Speech API**: Röstinmatning på svenska

### Backend
- **Python 3.7+**: Huvudspråk
- **Supabase**: Molnbaserad PostgreSQL-databas (persistent lagring)
- **SQLite**: Lokal cache för snabb åtkomst
- **Pandas**: Datahantering
- **Automatisk synkronisering**: Mellan lokal cache och molndatabas

### AI/ML
- **Groq API**: Llama 3.3 70B Versatile modell
- **Intelligent bokning**: Förstår naturligt språk och bokar automatiskt
- **Kontextmedveten**: Känner till kalenderns aktuella tillstånd
- **Gratis & Snabbt**: Ingen kostnad via Groq API, 10-100x snabbare än traditionella API:er

### Databas-schema
```sql
events (
  id INTEGER PRIMARY KEY,
  user TEXT,
  date TEXT,
  time TEXT,
  duration INTEGER DEFAULT 1,
  title TEXT,
  description TEXT,
  created_at TIMESTAMP,
  repeat_pattern TEXT,
  repeat_until TEXT,
  reminder BOOLEAN DEFAULT FALSE,
  reminder_sent BOOLEAN DEFAULT FALSE
)
```

## AI-funktionalitet

### Groq API (Llama 3.3 70B Versatile)
- **Kraftfull språkförståelse**: 70B parametrar för intelligent hantering
- **Svenska språket**: Utmärkt förståelse för svenska instruktioner
- **Kontextmedveten**: Känner till hela kalenderns tillstånd
- **100% Gratis**: Ingen kostnad via Groq API
- **Extremt Snabbt**: 10-100x snabbare än Hugging Face och OpenAI
- **Fungerar överallt**: Desktop, mobil, tablet - ingen lokal GPU krävs

### Kapabiliteter
- Extraherar datum: "17e oktober", "den 17", "imorgon", "nästa vecka", "på fredag"
- Identifierar användare: Albin, Maria, Familj
- Förstår komplexa frågor: "När är Maria ledig på fredag?"
- Intelligent bokning: "Boka lunch för Maria imorgon kl 12 i 2 timmar"
- Automatisk bokning via: `BOOK_EVENT|user|date|time|title|desc|duration`

## Projektstruktur

```
familjekalender/
├── app.py                    # Huvudapplikation
├── familjekalender.db        # SQLite-databas
├── requirements.txt          # Python-beroenden
├── manifest.json            # PWA-konfiguration
├── .streamlit/
│   ├── secrets.toml         # API-nycklar (ej i git)
│   └── secrets.toml.example # Template för secrets
├── calendar_component/      # Custom Streamlit-komponent (oanvänd)
│   ├── __init__.py
│   └── frontend/
│       └── index.html
└── README.md
```

## Deployment

### Streamlit Cloud
1. Pusha till GitHub
2. Koppla repository till Streamlit Cloud
3. Lägg till `HUGGINGFACE_API_KEY` i Streamlit Cloud secrets (valfritt)

### Lokal nätverksåtkomst
```bash
streamlit run app.py --server.address 0.0.0.0
```
Familjemedlemmar kan då komma åt på: `http://DIN-IP:8501`

## Utveckling

### Senaste uppdateringar (Oktober 2025)
- ✅ **Telegram-påminnelser fixade (2025-10-19)**
  - Diagnostiserade och löste problemet med utebliva påminnelser
  - Supabase-tabellen behövde kolumnen `reminder_sent` (BOOLEAN DEFAULT FALSE)
  - GitHub Actions secrets behövde konfigureras (SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_*)
  - Telegram-boten verifierad och fungerande - skickar meddelanden perfekt till Albin och Maria
  - GitHub Actions workflow kör varje 5:e minut och skickar påminnelser 15 min innan händelser
- ✅ **Supabase molndatabas** - Persistent lagring som överlever Streamlit Cloud restart
  - Händelser försvinner aldrig mer!
  - Automatisk synkronisering mellan lokal cache och molnet
  - Gratis PostgreSQL-databas med oändlig kapacitet för familjekalender
  - Import-verktyg för befintliga händelser
- ✅ **Telegram-påminnelser** - FUNGERAR FULLT UT
  - Push-notiser till telefonen 15 min innan händelser
  - Testad och verifierad för Albin och Maria
  - 100% gratis via Telegram Bot API
  - Fungerar även när appen är stängd
  - Multi-användare support för hela familjen
- ✅ **Uppgraderad till Qwen 2.5 72B Instruct** - 9x kraftfullare AI via Hugging Face
- ✅ **API-baserad AI** - Fungerar på alla enheter (desktop, mobil, tablet)
- ✅ **Sticky AI-chat** - Röstknapp + textinput följer med längst ner (chatbot-stil)
  - Förstärkt CSS med !important och z-index 999999 för att överrida Streamlit
  - Flera selektorvarianter för maximal kompatibilitet
- ✅ **Komplett UI återställd** - Veckovisning, färger, återkommande händelser
- ✅ Återkommande händelser med slutdatum
- ✅ Session state-fix för Streamlit
- ✅ Förbättrad mobil-responsivitet

### Kommande funktioner
- [ ] Exportera till iCal/Google Calendar
- [ ] Dela kalenderlänk med familjemedlemmar
- [ ] Mörkt tema
- [ ] Flera påminnelsetider (1 dag, 1 timme, 15 min)

## Licens

MIT License - fritt att använda och modifiera

## Kontakt

GitHub: [@albjo840](https://github.com/albjo840)
