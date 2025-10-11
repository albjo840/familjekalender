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

För att aktivera AI-assistenten:

1. Skapa ett gratis konto på Hugging Face: https://huggingface.co/join
2. Skapa en API-nyckel: https://huggingface.co/settings/tokens
3. Skapa en `.streamlit/secrets.toml` fil (kopiera från secrets.toml.example)
4. Lägg till din Hugging Face API-nyckel:
```toml
HUGGINGFACE_API_KEY = "hf_xxxxxxxxxxxxx"
```

Modell som används: **Qwen 2.5 72B Instruct** (gratis via Hugging Face Inference API)

## Funktioner

### Kalender
- **Veckovisning**: Måndag-Söndag, 7:00-22:00
- **5 användare**: Albin, Maria, Olle, Ellen, Familj
- **Färgkodning**: Unik gradient för varje användare
- **Varaktighet**: Händelser kan vara 1-12 timmar långa
- **Återkommande händelser**: Veckovisa upprepningar med slutdatum

### AI-Assistent
- **Röstinmatning**: Web Speech API med svensk språkstöd
- **Smart frågehantering**:
  - "Vad gör Albin 17e oktober?" → Filtrerar på användare och datum
  - "Vad finns bokat nästa vecka?" → Visar alla händelser
  - "När är Maria ledig på fredag?" → Analyserar lediga tider
- **Bokningar via naturligt språk**:
  - "Boka lunch för Maria imorgon kl 12"
  - "Lägg till tandläkare för Albin på fredag 14:00"
  - "Skapa familjemiddag på lördag 18:00 i 2 timmar"

### Händelsehantering
- **Lägg till händelser**: Via formulär eller AI-assistent
- **Redigera händelser**: Ändra tid, varaktighet, beskrivning
- **Ta bort händelser**: Enskilda eller alla förekomster av återkommande händelser
- **Veckonavigation**: Enkel navigering mellan veckor

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
- **SQLite**: Lokal databas för händelser
- **Pandas**: Datahantering

### AI/ML
- **Hugging Face Inference API**: Qwen 2.5 72B Instruct modell
- **Intelligent bokning**: Förstår naturligt språk och bokar automatiskt
- **Kontextmedveten**: Känner till kalenderns aktuella tillstånd
- **Gratis**: Ingen kostnad via Hugging Face Inference API

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
  repeat_until TEXT
)
```

## AI-funktionalitet

### Hugging Face Inference API (Qwen 2.5 72B Instruct)
- **Kraftfull språkförståelse**: 72B parametrar för intelligent hantering
- **Svenska språket**: Utmärkt förståelse för svenska instruktioner
- **Kontextmedveten**: Känner till hela kalenderns tillstånd
- **Gratis**: Ingen kostnad via Hugging Face Inference API
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

### Senaste uppdateringar
- ✅ **Uppgraderad till Qwen 2.5 72B Instruct** - Kraftfull AI via Hugging Face
- ✅ **API-baserad AI** - Fungerar på alla enheter (desktop, mobil, tablet)
- ✅ Återkommande händelser
- ✅ Session state-fix för Streamlit
- ✅ Förbättrad mobil-responsivitet

### Kommande funktioner
- [ ] Notifikationer
- [ ] Exportera till iCal/Google Calendar
- [ ] Dela kalenderlänk med familjemedlemmar
- [ ] Mörkt tema

## Licens

MIT License - fritt att använda och modifiera

## Kontakt

GitHub: [@albjo840](https://github.com/albjo840)
