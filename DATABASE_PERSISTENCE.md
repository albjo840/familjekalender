# 🔒 Database Persistence System

## Problem
Streamlit Cloud och vissa hosting-miljöer kan återställa filsystemet när appen är inaktiv, vilket kan leda till dataförlust.

## Lösning
Ett hybridlagringssystem som automatiskt säkerhetskopierar och återställer data:

### 🎯 Funktioner

1. **Automatisk JSON-backup**
   - Varje gång en händelse läggs till, redigeras eller tas bort
   - Sparas som `familjekalender.db.json` i projektmappen
   - Innehåller alla händelser med fullständig metadata

2. **Automatisk återställning vid start**
   - När appen startar kontrolleras om databasen är tom
   - Om tom: återställs automatiskt från JSON-backup
   - Om data finns: skapar ny backup för säkerhet

3. **Dubbel säkerhet**
   - SQLite `.backup` fil (traditionell metod)
   - JSON backup (mer portabel och pålitlig)

### 📁 Filer

```
familjekalender/
├── familjekalender.db           # Huvuddatabas (SQLite)
├── familjekalender.db.backup    # SQLite backup
├── familjekalender.db.json      # JSON backup (mest pålitlig)
└── db_persistence.py            # Persistence layer
```

### 🔄 Hur det fungerar

```
1. Användare lägger till händelse
   ↓
2. Sparas i SQLite (familjekalender.db)
   ↓
3. Automatisk backup till .json OCH .backup
   ↓
4. Streamlit går i viloläge (database raderas)
   ↓
5. Användare öppnar appen igen
   ↓
6. init_database() körs
   ↓
7. create_persistent_db() kontrollerar databasen
   ↓
8. Ser att den är tom → återställer från .json
   ↓
9. ✅ Alla händelser är tillbaka!
```

### 🛠️ Implementation

**app.py:**
```python
from db_persistence import create_persistent_db

# Vid initialization
db_persistence = create_persistent_db(DB_PATH)

# Vid varje ändring
backup_database()  # Skapar både .backup och .json
```

**db_persistence.py:**
```python
class DatabasePersistence:
    def backup_to_json()      # Spara till JSON
    def restore_from_json()   # Återställ från JSON
    def check_and_restore()   # Automatisk kontroll vid start
```

### ✅ Testresultat

```
✓ JSON backup skapas korrekt (1364 bytes, 4 händelser)
✓ Restore fungerar från tom databas
✓ Automatisk kontroll vid start fungerar
✓ App initierar korrekt med persistence
```

### 📊 Backup-format (JSON)

```json
{
  "backup_time": "2025-10-13T19:35:10.536077",
  "events": [
    {
      "id": 36,
      "user": "Olle",
      "date": "2025-10-06",
      "time": "11:00",
      "duration": 1,
      "title": "Jiu-jitsu",
      "description": "Kampsportsträning",
      "created_at": "2025-10-09 19:53:35",
      "repeat_pattern": "sön",
      "repeat_until": "2026-01-04",
      "reminder": 0
    }
  ]
}
```

### 🚀 Framtida förbättringar

- [ ] **Google Sheets integration** - Synka till molnet automatiskt
- [ ] **Supabase support** - Gratis PostgreSQL i molnet
- [ ] **Dropbox/Google Drive** - Automatisk molnbackup
- [ ] **Versionering** - Spara flera versioner av backuper
- [ ] **Kryptering** - Krypterade backuper för känslig data

### 🔧 Manuell återställning

Om något går fel kan du manuellt återställa:

```bash
# Från JSON backup
python3 << EOF
from db_persistence import create_persistent_db
persistence = create_persistent_db('familjekalender.db')
persistence.restore_from_json()
EOF

# Från SQLite backup
cp familjekalender.db.backup familjekalender.db
```

### 🎉 Resultat

**Före:** Data försvinner när Streamlit går i viloläge
**Efter:** Data återställs automatiskt när appen vaknar

**Ingen användarinteraktion krävs** - systemet är helt automatiskt!
