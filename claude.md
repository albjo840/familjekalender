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

### Konfiguration (valfritt)

För att aktivera Hugging Face AI-assistent istället för regelbaserad AI:

1. Skapa en `.streamlit/secrets.toml` fil
2. Lägg till din Hugging Face API-nyckel:
```toml
HUGGINGFACE_API_KEY = "hf_xxxxxxxxxxxxx"
```

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
- **Regelbaserad AI** (fallback): Pattern matching för datum, tid, användare
- **Hugging Face API** (valfritt): Zephyr-7b-beta modell för naturlig språkförståelse

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

### Regelbaserad AI (aktiv utan API-nyckel)
- Extraherar datum: "17e oktober", "den 17", "imorgon", "övermorgon"
- Identifierar användare: automatisk igenkänning av namn
- Skiljer frågor från bokningar via nyckelord:
  - **Frågor**: vad, när, vilken, visa, hitta, har, finns
  - **Bokningar**: boka, lägg till, skapa, planera

### Hugging Face AI (kräver API-nyckel)
- Använder **Zephyr-7b-beta** modell (öppen licens)
- Förstår komplex naturlig språk
- Intelligent bokning via `BOOK_EVENT|user|date|time|title|desc|duration`
- Bättre kontext-förståelse för komplexa frågor

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
- ✅ Regelbaserad AI med datumfiltrering
- ✅ AI skiljer frågor från bokningar
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
