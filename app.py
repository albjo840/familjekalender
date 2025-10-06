import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import calendar
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import html

# Konfigurera sidan
st.set_page_config(
    page_title="Familjekalender",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS för Apple-liknande design med drag-funktionalitet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');

    html, body, .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    .main {
        padding: 0.5rem;
        background: transparent;
    }

    /* Mobil responsivitet */
    @media (max-width: 768px) {
        .main {
            padding: 0.25rem;
        }

        .stColumn {
            padding: 0 1px !important;
            min-width: 0 !important;
        }

        /* Kompakta rubriker på mobil */
        h1 {
            font-size: 1.5rem !important;
        }

        /* Mindre färgförklaringar */
        .legend-item {
            font-size: 10px !important;
        }

        /* Kompakt kalendervy */
        div[data-testid="column"] > div {
            padding: 1px !important;
        }

        /* Mindre knappar */
        button {
            font-size: 12px !important;
            padding: 4px 8px !important;
        }

        /* Ta bort onödiga marginaler */
        .stButton button {
            margin: 0 !important;
        }
    }

    .calendar-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.06);
        margin: 16px 0;
        overflow: hidden;
    }

    .calendar-time {
        background: rgba(248, 249, 250, 0.6);
        padding: 16px 10px;
        text-align: center;
        font-weight: 400;
        font-size: 12px;
        color: #8e8e93;
        border-right: 1px solid rgba(0, 0, 0, 0.04);
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 0;
    }

    .calendar-cell {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(0, 0, 0, 0.04);
        min-height: 80px;
        padding: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        border-radius: 0;
    }

    .calendar-cell:hover {
        background: rgba(0, 122, 255, 0.03);
        border-color: rgba(0, 122, 255, 0.15);
    }

    .calendar-header {
        background: rgba(248, 249, 250, 0.95);
        color: #1d1d1f;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 13px;
        border-radius: 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }

    .calendar-date {
        font-size: 10px;
        color: #8e8e93;
        font-weight: 400;
        margin-top: 2px;
    }

    @media (max-width: 768px) {
        .calendar-header {
            padding: 8px 4px;
            font-size: 11px;
        }

        .calendar-date {
            font-size: 9px;
        }
    }

    .event {
        border-radius: 6px;
        padding: 6px 8px;
        margin: 4px 0;
        font-size: 12px;
        font-weight: 500;
        line-height: 1.3;
        cursor: pointer;
        transition: all 0.2s ease;
        position: relative;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
        min-height: 24px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .event:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    @media (max-width: 768px) {
        .event {
            padding: 4px 6px;
            font-size: 10px;
            min-height: 20px;
            margin: 2px 0;
        }
    }

    .user-albin {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        animation: pulse 2s ease-in-out infinite;
    }

    .user-maria {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        animation: pulse 2s ease-in-out infinite;
    }

    .user-familj {
        background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        50% {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        }
    }

    .event-multi-hour {
        background: linear-gradient(to bottom, var(--event-color) 0%, var(--event-color-dark) 100%);
        border-left: 4px solid var(--event-accent);
    }

    .resize-handle {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 8px;
        background: rgba(255, 255, 255, 0.3);
        cursor: ns-resize;
        opacity: 0;
        transition: opacity 0.2s;
        border-radius: 0 0 8px 8px;
    }

    .event:hover .resize-handle {
        opacity: 1;
    }

    .resize-handle:hover {
        background: rgba(255, 255, 255, 0.5);
    }

    .add-event-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 32px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        min-width: 380px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        z-index: 999;
    }

    .user-legend {
        display: flex;
        gap: 24px;
        justify-content: center;
        margin: 12px 0;
        padding: 16px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        flex-wrap: wrap;
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        font-weight: 500;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }

    .legend-color {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    @media (max-width: 768px) {
        .user-legend {
            gap: 16px;
            padding: 12px;
        }

        .legend-item {
            font-size: 12px;
            gap: 6px;
        }

        .legend-color {
            width: 12px;
            height: 12px;
        }
    }

    .legend-albin {
        background: linear-gradient(135deg, #34c759 0%, #30d158 100%);
    }
    .legend-maria {
        background: linear-gradient(135deg, #ff9500 0%, #ff6b35 100%);
    }
    .legend-familj {
        background: linear-gradient(135deg, #af52de 0%, #5856d6 100%);
    }

    .duration-selector {
        background: rgba(0, 122, 255, 0.1);
        border: 2px solid #007aff;
        border-radius: 12px;
        padding: 8px 12px;
        margin: 8px 0;
        font-weight: 500;
        color: #007aff;
    }

    /* Drag och drop visuella effekter */
    .drop-zone {
        background: rgba(0, 122, 255, 0.1);
        border: 2px dashed #007aff;
        border-radius: 8px;
    }

    .drop-zone-active {
        background: rgba(0, 122, 255, 0.2);
        border-color: #0056b3;
    }

    /* Apple-liknande knappar */
    .apple-button {
        background: linear-gradient(135deg, #007aff 0%, #0056b3 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
    }

    .apple-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 122, 255, 0.4);
    }

    .apple-button-secondary {
        background: rgba(142, 142, 147, 0.1);
        color: #1d1d1f;
        border: 1px solid rgba(142, 142, 147, 0.2);
    }

</style>
""", unsafe_allow_html=True)

# Hjälpfunktion för säker event-unpacking
def safe_unpack_event(event):
    """Säkert unpacking av event oavsett antal kolumner"""
    # Standard struktur: id, user, date, time, duration, title, description, created_at, repeat_pattern, repeat_until
    defaults = {
        'id': None,
        'user': '',
        'date': '',
        'time': '',
        'duration': 1,
        'title': '',
        'description': '',
        'created_at': '',
        'repeat_pattern': None,
        'repeat_until': None
    }

    if len(event) >= 10:
        return {
            'id': event[0],
            'user': event[1],
            'date': event[2],
            'time': event[3],
            'duration': event[4] or 1,
            'title': event[5],
            'description': event[6] or '',
            'created_at': event[7] or '',
            'repeat_pattern': event[8],
            'repeat_until': event[9]
        }
    elif len(event) >= 8:
        return {
            'id': event[0],
            'user': event[1],
            'date': event[2],
            'time': event[3],
            'duration': event[4] or 1,
            'title': event[5],
            'description': event[6] or '',
            'created_at': event[7] or '',
            'repeat_pattern': None,
            'repeat_until': None
        }
    elif len(event) >= 7:
        return {
            'id': event[0],
            'user': event[1],
            'date': event[2],
            'time': event[3],
            'title': event[4],
            'description': event[5] or '',
            'created_at': event[6] or '',
            'duration': 1,
            'repeat_pattern': None,
            'repeat_until': None
        }
    else:
        return defaults

# Databas-funktioner
def init_database():
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            duration INTEGER DEFAULT 1,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Lägg till duration-kolumn om den inte finns
    c.execute("PRAGMA table_info(events)")
    columns = [column[1] for column in c.fetchall()]
    if 'duration' not in columns:
        c.execute('ALTER TABLE events ADD COLUMN duration INTEGER DEFAULT 1')
    if 'repeat_pattern' not in columns:
        c.execute('ALTER TABLE events ADD COLUMN repeat_pattern TEXT DEFAULT NULL')
    if 'repeat_until' not in columns:
        c.execute('ALTER TABLE events ADD COLUMN repeat_until TEXT DEFAULT NULL')
    conn.commit()
    conn.close()

def add_event(user, date, time, title, description="", duration=1, repeat_pattern=None, repeat_until=None):
    # Input validering
    import re
    VALID_USERS = ["Albin", "Maria", "Olle", "Ellen", "Familj"]
    VALID_REPEAT_PATTERNS = ['mån', 'tis', 'ons', 'tor', 'fre', 'lör', 'sön', None]

    if user not in VALID_USERS:
        raise ValueError(f"Ogiltig användare: {user}. Måste vara en av {', '.join(VALID_USERS)}")

    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Ogiltigt datumformat: {date}. Använd YYYY-MM-DD")

    if not re.match(r'^\d{2}:\d{2}$', time):
        raise ValueError(f"Ogiltigt tidformat: {time}. Använd HH:MM")

    if not title or len(title.strip()) == 0:
        raise ValueError("Titel kan inte vara tom")

    if duration < 1 or duration > 12:
        raise ValueError(f"Duration måste vara mellan 1 och 12 timmar, fick {duration}")

    if repeat_pattern and repeat_pattern not in VALID_REPEAT_PATTERNS:
        raise ValueError(f"Ogiltigt repeat_pattern: {repeat_pattern}. Måste vara en av {', '.join([p for p in VALID_REPEAT_PATTERNS if p])}")

    if repeat_until:
        try:
            datetime.strptime(repeat_until, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Ogiltigt repeat_until format: {repeat_until}. Använd YYYY-MM-DD")

    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO events (user, date, time, title, description, duration, repeat_pattern, repeat_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user, date, time, title, description, duration, repeat_pattern, repeat_until))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def update_event_duration(event_id, new_duration):
    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()
        c.execute('UPDATE events SET duration = ? WHERE id = ?', (new_duration, event_id))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_events_for_week(start_date):
    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()

        end_date = start_date + timedelta(days=6)
        c.execute('''
            SELECT * FROM events
            WHERE date BETWEEN ? AND ?
            ORDER BY date, time
        ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

        events = c.fetchall()
        return events
    finally:
        if conn:
            conn.close()

def get_events_for_month(year, month):
    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()

        # Första och sista dagen i månaden
        first_day = datetime(year, month, 1).date()
        if month == 12:
            last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

        # Optimerad SQL: Hämta bara relevanta events (inkl. återkommande som kan visas i månaden)
        c.execute('''
            SELECT * FROM events
            WHERE (date BETWEEN ? AND ?)
               OR (repeat_pattern IS NOT NULL AND date <= ?)
            ORDER BY date, time
        ''', (first_day.strftime('%Y-%m-%d'),
              last_day.strftime('%Y-%m-%d'),
              last_day.strftime('%Y-%m-%d')))
        all_events = c.fetchall()
    finally:
        if conn:
            conn.close()

    # Expandera återkommande händelser
    expanded_events = []
    for event in all_events:
        e = safe_unpack_event(event)
        event_date = datetime.strptime(e['date'], '%Y-%m-%d').date()

        if e['repeat_pattern']:  # Återkommande händelse
            repeat_end = datetime.strptime(e['repeat_until'], '%Y-%m-%d').date() if e['repeat_until'] else last_day
            weekday_map = {'mån': 0, 'tis': 1, 'ons': 2, 'tor': 3, 'fre': 4, 'lör': 5, 'sön': 6}

            if e['repeat_pattern'] in weekday_map:
                target_weekday = weekday_map[e['repeat_pattern']]
                current_date = event_date
                while current_date <= min(repeat_end, last_day):
                    if current_date >= first_day and current_date.weekday() == target_weekday:
                        expanded_events.append((
                            e['id'], e['user'], current_date.strftime('%Y-%m-%d'), e['time'],
                            e['duration'], e['title'], e['description'], e['created_at'],
                            e['repeat_pattern'], e['repeat_until']
                        ))
                    current_date += timedelta(days=1)
            else:
                # Ingen giltig repeat pattern, lägg till som vanlig
                if first_day <= event_date <= last_day:
                    expanded_events.append(event)
        else:
            # Vanlig händelse utan repetering
            if first_day <= event_date <= last_day:
                expanded_events.append(event)

    return expanded_events

def delete_event(event_id):
    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()
        c.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

# AI-hjälpfunktioner
def get_calendar_context(year, month):
    """Hämtar kalenderdata för AI-kontext"""
    events = get_events_for_month(year, month)

    context = f"Kalenderdata för {year}-{month:02d}:\n\n"

    if not events:
        context += "Inga händelser denna månad.\n"
    else:
        for event in events:
            e = safe_unpack_event(event)
            context += f"- {e['date']} kl {e['time']}: {e['title']} ({e['user']})"
            if e['description']:
                context += f" - {e['description']}"
            try:
                dur = int(e['duration']) if e['duration'] else 1
                if dur > 1:
                    context += f" [{dur} timmar]"
            except (ValueError, TypeError):
                pass
            context += "\n"

    return context

def get_available_times(date_str, user=None):
    """Hittar lediga tider för ett givet datum"""
    conn = None
    try:
        conn = sqlite3.connect('familjekalender.db')
        c = conn.cursor()

        if user:
            c.execute('SELECT time, duration FROM events WHERE date = ? AND user = ? ORDER BY time',
                     (date_str, user))
        else:
            c.execute('SELECT time, duration FROM events WHERE date = ? ORDER BY time',
                     (date_str,))

        booked_events = c.fetchall()
    finally:
        if conn:
            conn.close()

    # Generera lista över lediga tider (07:00-22:00)
    all_hours = [f"{h:02d}:00" for h in range(7, 23)]
    booked_hours = set()

    for time_str, duration in booked_events:
        hour = int(time_str.split(':')[0])
        try:
            dur = int(duration) if duration else 1
        except:
            dur = 1
        for i in range(dur):
            booked_hours.add(f"{hour + i:02d}:00")

    available = [h for h in all_hours if h not in booked_hours]
    return available

def ai_book_event(user, date, time, title, description="", duration=1):
    """Funktion som AI kan anropa för att boka händelser"""
    try:
        add_event(user, date, time, title, description, duration)
        return f"✓ Bokad: {title} för {user} den {date} kl {time}"
    except Exception as e:
        return f"✗ Fel vid bokning: {str(e)}"

@st.cache_resource
def load_local_model():
    """Laddar GPT-modellen lokalt med GPU-stöd"""
    try:
        # Använd Llama-3-8B-Instruct - redan nedladdad, utmärkt för function calling
        model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

        device = "cuda" if torch.cuda.is_available() else "cpu"

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Llama saknar pad_token, sätt det till eos_token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        dtype = torch.float16 if device == "cuda" else torch.float32

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            dtype=dtype,
            device_map="auto",
            low_cpu_mem_usage=True
        )

        return model, tokenizer, device
    except Exception as e:
        st.error(f"Kunde inte ladda modell: {str(e)}")
        return None, None, None

def call_gpt_local(user_message, year, month):
    """Anropar GPT lokalt på GPU"""

    # Hämta kalenderkontext
    calendar_context = get_calendar_context(year, month)

    # Systemmeddelande med instruktioner
    today = datetime.now()
    system_message = f"""Du är en intelligent kalenderassistent för en familjekalender.

ANVÄNDARE: Albin, Maria, Familj

DAGENS DATUM: {today.strftime('%Y-%m-%d')} ({today.strftime('%A, %d %B %Y')})

AKTUELL KALENDER ({year}-{month:02d}):
{calendar_context}

DINA UPPGIFTER:
1. Svara på frågor om kalendern (vad finns bokat, lediga tider, etc.)
2. Boka händelser när användaren ber om det
3. Förstå relativa datum (imorgon, nästa vecka, på fredag, etc.)

VIKTIGT - NÄR ANVÄNDAREN BER DIG BOKA/LÄGGA TILL/SKAPA EN HÄNDELSE:
Du MÅSTE använda BOOK_EVENT-kommandot! Formatet är exakt:
BOOK_EVENT|användare|YYYY-MM-DD|HH:MM|titel|beskrivning|varaktighet_timmar

EXEMPEL PÅ BOKNINGAR:
- "Boka lunch med Maria imorgon kl 12" → BOOK_EVENT|Maria|{(today + timedelta(days=1)).strftime('%Y-%m-%d')}|12:00|Lunch|Lunch möte|1
- "Lägg till tandläkare för Albin på fredag 14:00" → BOOK_EVENT|Albin|[fredag-datum]|14:00|Tandläkare||1
- "Skapa familjemiddag på lördag 18:00 i 2 timmar" → BOOK_EVENT|Familj|[lördag-datum]|18:00|Familjemiddag||2

REGLER:
- Använd alltid formatet YYYY-MM-DD för datum
- Använd HH:MM för tid (24-timmars format)
- Varaktighet i hela timmar (default: 1)
- Beskrivning kan vara tom om inget anges
- Svar alltid på svenska
- Om datum är oklart, fråga användaren

När du har använt BOOK_EVENT, bekräfta bokningen på ett vänligt sätt!"""

    # Ladda modell
    model, tokenizer, device = load_local_model()

    if model is None:
        return "⚠️ Kunde inte ladda AI-modellen. Kontrollera GPU-konfigurationen."

    try:
        # Skapa Qwen2.5 chat format
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        # Använd tokenizers chat template
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenisera
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(device)

        # Generera svar
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=350,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id if tokenizer.pad_token_id else tokenizer.eos_token_id
            )

        # Dekoda svaret
        response = tokenizer.decode(outputs[0], skip_special_tokens=False)

        # Extrahera bara assistentens svar för Llama-3
        if "<|start_header_id|>assistant<|end_header_id|>" in response:
            ai_response = response.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
            if "<|eot_id|>" in ai_response:
                ai_response = ai_response.split("<|eot_id|>")[0].strip()
        elif user_message in response:
            ai_response = response.split(user_message)[-1].strip()
        else:
            # Fallback: ta bort input från output
            input_length = inputs['input_ids'].shape[1]
            ai_response = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True).strip()

        # Kontrollera om AI:n vill boka en händelse
        if "BOOK_EVENT|" in ai_response:
            try:
                # Extrahera BOOK_EVENT-kommandot (ta bara första raden om det finns flera)
                book_line = ai_response.split("BOOK_EVENT|")[1].split("\n")[0]
                parts = book_line.split("|")

                if len(parts) < 4:
                    ai_response += "\n\n⚠️ Fel format på BOOK_EVENT kommando (behöver minst user|date|time|title)."
                    return ai_response

                user, date, time, title = parts[:4]

                # Validera datum format
                import re
                try:
                    datetime.strptime(date.strip(), '%Y-%m-%d')
                except ValueError:
                    ai_response += f"\n\n⚠️ Ogiltigt datumformat: {date}. Använd YYYY-MM-DD."
                    return ai_response

                # Validera tid format
                if not re.match(r'^\d{2}:\d{2}$', time.strip()):
                    ai_response += f"\n\n⚠️ Ogiltigt tidformat: {time}. Använd HH:MM."
                    return ai_response

                # Validera user
                valid_users = ["Albin", "Maria", "Olle", "Ellen", "Familj"]
                if user.strip() not in valid_users:
                    ai_response += f"\n\n⚠️ Ogiltig användare: {user}. Måste vara en av {', '.join(valid_users)}."
                    return ai_response

                description = parts[4].strip() if len(parts) > 4 else ""

                # Hantera duration säkert
                duration = 1
                if len(parts) > 5:
                    duration_str = parts[5].strip()
                    match = re.match(r'^\d+', duration_str)
                    if match:
                        duration = min(int(match.group()), 12)  # Max 12 timmar

                booking_result = ai_book_event(user.strip(), date.strip(), time.strip(),
                                               title.strip(), description, duration)

                # Ta bort BOOK_EVENT-kommandot från svaret
                ai_response = ai_response.split("BOOK_EVENT|")[0].strip() + "\n\n" + booking_result

            except Exception as e:
                ai_response += f"\n\n⚠️ Fel vid bokning: {str(e)}"

        return ai_response

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"⚠️ Fel vid AI-generering: {str(e)}\n\nDetaljer: {error_details[:200]}"

# Huvudapplikation
def main():
    # Initiera databas
    init_database()

    # Titel och färgförklaring
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.15); border-radius: 16px; padding: 1.5rem;
                backdrop-filter: blur(10px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
        <h1 style="color: white; text-align: center; margin-bottom: 1rem; font-size: 2.5rem; font-weight: 700;">
            📅 Familjekalender
        </h1>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; border-radius: 4px;
                            background: linear-gradient(135deg, #34c759 0%, #30d158 100%);"></div>
                <span style="color: white; font-size: 14px;">Albin</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; border-radius: 4px;
                            background: linear-gradient(135deg, #ff9500 0%, #ff6b35 100%);"></div>
                <span style="color: white; font-size: 14px;">Maria</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; border-radius: 4px;
                            background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);"></div>
                <span style="color: white; font-size: 14px;">Olle</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; border-radius: 4px;
                            background: linear-gradient(135deg, #ff2d55 0%, #ff375f 100%);"></div>
                <span style="color: white; font-size: 14px;">Ellen</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="width: 16px; height: 16px; border-radius: 4px;
                            background: linear-gradient(135deg, #af52de 0%, #5856d6 100%);"></div>
                <span style="color: white; font-size: 14px;">Familj</span>
            </div>
        </div>
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="color: white; text-align: center; font-size: 0.95rem; margin-bottom: 0;">
                🤖 <strong>AI-Assistent</strong> - Fråga eller boka via röst/text nedan
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initiera chat historik
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Initiera röstinmatning state
    if 'voice_input' not in st.session_state:
        st.session_state['voice_input'] = ""

    # Aktuell månad som default
    today = datetime.now().date()

    # Använd current_month från session state om den finns
    if 'current_month' not in st.session_state:
        st.session_state['current_month'] = today.month
        st.session_state['current_year'] = today.year

    # Initiera current_week om det inte finns
    if 'current_week' not in st.session_state:
        today = datetime.now().date()
        st.session_state['current_week'] = today - timedelta(days=today.weekday())

    # Navigation i toppen - veckonavigering
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])

    with nav_col1:
        if st.button("⬅️", use_container_width=True):
            st.session_state['current_week'] -= timedelta(days=7)
            st.rerun()

    with nav_col2:
        week_start = st.session_state['current_week']
        week_end = week_start + timedelta(days=6)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'Maj', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dec']
        st.markdown(f"""
        <div style='text-align:center;font-weight:600;font-size:1.2rem;color:white;padding:8px;
                    background:rgba(255,255,255,0.1);border-radius:12px;backdrop-filter:blur(10px);'>
            {week_start.day} {month_names[week_start.month-1]} - {week_end.day} {month_names[week_end.month-1]} {week_end.year}
        </div>
        """, unsafe_allow_html=True)

    with nav_col3:
        if st.button("➡️", use_container_width=True):
            st.session_state['current_week'] += timedelta(days=7)
            st.rerun()

    # Röstinmatning med Web Speech API - kompakt
    st.markdown("""
    <div id="voice-input-container" style="text-align: center; margin-bottom: 0.5rem;">
        <button id="voice-button" onclick="startVoiceRecognition()"
                style="background: linear-gradient(135deg, #5856d6 0%, #af52de 100%);
                       color: white; border: none; border-radius: 50%; width: 44px; height: 44px;
                       font-size: 20px; cursor: pointer; box-shadow: 0 2px 8px rgba(88,86,214,0.3);
                       transition: all 0.3s ease;">
            🎤
        </button>
        <p id="voice-status" style="color: white; margin-top: 0.3rem; font-size: 11px;"></p>
    </div>

    <script>
    let recognition;
    let isRecording = false;

    function startVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert('Röstinmatning stöds inte i din webbläsare. Använd Chrome eller Edge.');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'sv-SE';
        recognition.continuous = false;
        recognition.interimResults = false;

        const button = document.getElementById('voice-button');
        const status = document.getElementById('voice-status');

        if (isRecording) {
            recognition.stop();
            button.style.background = 'linear-gradient(135deg, #5856d6 0%, #af52de 100%)';
            button.textContent = '🎤';
            status.textContent = '';
            isRecording = false;
            return;
        }

        recognition.onstart = function() {
            isRecording = true;
            button.style.background = 'linear-gradient(135deg, #34c759 0%, #30d158 100%)';
            button.textContent = '⏹️';
            status.textContent = 'Lyssnar... Prata nu!';
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            status.textContent = 'Bearbetar: "' + transcript + '"';

            // Sätt input i Streamlit text input
            const textInput = window.parent.document.querySelector('input[aria-label="🤖 Fråga AI-assistenten eller boka händelse:"]');
            if (textInput) {
                textInput.value = transcript;
                textInput.dispatchEvent(new Event('input', { bubbles: true }));
                textInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        };

        recognition.onerror = function(event) {
            button.style.background = 'linear-gradient(135deg, #5856d6 0%, #af52de 100%)';
            button.textContent = '🎤';
            status.textContent = 'Fel: ' + event.error;
            isRecording = false;
        };

        recognition.onend = function() {
            button.style.background = 'linear-gradient(135deg, #5856d6 0%, #af52de 100%)';
            button.textContent = '🎤';
            isRecording = false;
        };

        recognition.start();
    }
    </script>
    """, unsafe_allow_html=True)

    # AI Sökruta - kompakt
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 0.5rem; margin: 0.5rem 0; backdrop-filter: blur(10px);">
    """, unsafe_allow_html=True)

    user_input = st.text_input("🤖 AI-assistent",
                                placeholder="Boka eller fråga...",
                                key="ai_search",
                                label_visibility="collapsed")

    st.markdown("</div>", unsafe_allow_html=True)

    if user_input:
        # Anropa AI:n (lokalt på GPU)
        with st.spinner('🤔 Tänker...'):
            ai_response = call_gpt_local(user_input, st.session_state['current_week'].year, st.session_state['current_week'].month)

        # Visa svaret tillfälligt med auto-dismiss
        if "✓" in ai_response:  # Om bokning genomfördes
            st.success(ai_response)
            # Rensa input och uppdatera kalendern omedelbart
            st.session_state['ai_search'] = ""
            st.rerun()
        else:
            # Visa svar för frågor
            st.info(ai_response)

    # Hämta händelser för aktuell vecka
    week_start = st.session_state['current_week']
    week_end = week_start + timedelta(days=6)

    # Använd månad från veckostart för att hämta events
    events = get_events_for_month(week_start.year, week_start.month)

    # Hämta även events från nästa månad om veckan går över månadsskifte
    if week_end.month != week_start.month:
        events_next_month = get_events_for_month(week_end.year, week_end.month)
        events = events + events_next_month

    # Skapa DataFrame för enklare hantering
    if events:
        # Kontrollera om duration finns i resultatet
        if len(events[0]) >= 10:  # Ny struktur med repeat
            # Korrekt ordning: id, user, date, time, title, description, created_at, duration, repeat_pattern, repeat_until
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'title', 'description', 'created_at', 'duration', 'repeat_pattern', 'repeat_until'])
        elif len(events[0]) >= 8:  # Struktur med duration
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'title', 'description', 'created_at', 'duration'])
        else:  # Gammal struktur utan duration
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'title', 'description', 'created_at'])
            events_df['duration'] = 1  # Sätt default duration
    else:
        events_df = pd.DataFrame(columns=['id', 'user', 'date', 'time', 'title', 'description', 'created_at', 'duration', 'repeat_pattern', 'repeat_until'])

    # Dialog för att lägga till händelse
    if 'show_add_dialog' not in st.session_state:
        st.session_state.show_add_dialog = False
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_time' not in st.session_state:
        st.session_state.selected_time = None
    if 'existing_events' not in st.session_state:
        st.session_state.existing_events = []

    # Veckokalendervy
    import calendar as cal

    # Hitta vilken vecka vi är på
    current_week_start = st.session_state['current_week']
    week_dates = [current_week_start + timedelta(days=i) for i in range(7)]

    # Veckodagar
    weekdays = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag', 'Lördag', 'Söndag']

    # Visa varje dag vertikalt
    for day_idx, date_obj in enumerate(week_dates):
        date_str = date_obj.strftime('%Y-%m-%d')
        day_num = date_obj.day
        weekday_name = weekdays[day_idx]

        # Kolla om det är idag
        is_today = date_obj == datetime.now().date()
        today_style = "border-left: 4px solid #4facfe;" if is_today else ""

        # Hämta händelser för denna dag
        day_events = events_df[events_df['date'] == date_str]

        # Rita dagkort
        st.markdown(f'''
        <div style="background:rgba(255,255,255,0.95);border-radius:12px;margin:8px 0;padding:12px;{today_style}box-shadow:0 4px 12px rgba(0,0,0,0.1);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-weight:700;font-size:18px;color:#333;">{weekday_name}</div>
                    <div style="font-size:14px;color:#666;">{day_num} {date_obj.strftime('%B %Y')}</div>
                </div>
                <div style="font-size:32px;font-weight:700;color:#4facfe;opacity:0.3;">{day_num}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Definiera färgmappning för användare
        user_colors = {
            'Albin': '#34c759',     # Grön
            'Maria': '#ff9500',     # Orange
            'Olle': '#007aff',      # Blå
            'Ellen': '#ff2d55',     # Röd
            'Familj': '#af52de'     # Lila
        }

        # Visa events som färgkodade boxar (ej klickbara)
        if not day_events.empty:
            for idx, event in day_events.iterrows():
                safe_title = html.escape(str(event['title']))
                event_time = event.get('time', '')
                event_user = event.get('user', '')
                event_id = event.get('id')

                # Beräkna sluttid
                try:
                    duration = int(event.get('duration', 1))
                except (ValueError, TypeError):
                    duration = 1
                start_hour = int(event_time.split(':')[0])
                end_hour = start_hour + duration
                end_time = f"{end_hour:02d}:00"
                time_range = f"{event_time} - {end_time}"

                bg_color = user_colors.get(event_user, '#8e8e93')

                # Färgad box (endast visuell)
                st.markdown(f'''
                <div style="background: {bg_color}; opacity: 0.85; color: white; padding: 12px 16px;
                            border-radius: 8px; margin: 6px 0; font-weight: 500;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.12);">
                    <div style="font-weight: 600; font-size: 13px;">{time_range}</div>
                    <div style="margin-top: 3px; font-size: 15px;">{safe_title}</div>
                </div>
                ''', unsafe_allow_html=True)

        # En gemensam knapp för både redigera och lägga till
        has_events = not day_events.empty
        button_text = "✏️ Hantera händelser" if has_events else "➕ Lägg till händelse"

        if st.button(button_text, key=f"manage_{date_str}", use_container_width=True, type="secondary"):
            st.session_state.show_add_dialog = True
            st.session_state.selected_date = date_str
            st.session_state.selected_time = day_events.iloc[0]['time'] if has_events else "09:00"
            existing = day_events.to_dict('records') if not day_events.empty else []
            st.session_state.existing_events = existing
            st.rerun()

        # Separator mellan dagar
        if day_idx < 6:
            st.markdown('<hr style="margin:16px 0;border:none;border-top:1px solid rgba(255,255,255,0.2);">', unsafe_allow_html=True)

    # Dialog för att lägga till/redigera händelse
    @st.dialog("Hantera händelser", width="large")
    def show_event_dialog():
        selected_date_obj = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').date()

        st.markdown(f"### 📅 {selected_date_obj.strftime('%A %d %B %Y')}")

        # Om det finns befintliga händelser, visa dem först
        if st.session_state.existing_events:
            st.divider()
            st.subheader("📋 Befintliga händelser")
            for event in st.session_state.existing_events:
                with st.expander(f"✏️ {event['title']} - {event['user']} ({event['time']})", expanded=False):
                    # Redigera händelse
                    users_list = ["Albin", "Maria", "Olle", "Ellen", "Familj"]
                    edit_user = st.selectbox("Vem:", users_list,
                                            index=users_list.index(event['user']) if event['user'] in users_list else 0,
                                            key=f"edit_user_{event['id']}")
                    edit_title = st.text_input("Titel:", value=event['title'], key=f"edit_title_{event['id']}")

                    col_e_start, col_e_end = st.columns(2)
                    with col_e_start:
                        edit_time = st.selectbox("Från:", [f"{h:02d}:00" for h in range(7, 23)],
                                                index=[f"{h:02d}:00" for h in range(7, 23)].index(event['time']),
                                                key=f"edit_time_{event['id']}")
                    with col_e_end:
                        current_duration = event.get('duration', 1)
                        try:
                            dur = int(current_duration) if current_duration else 1
                        except (ValueError, TypeError):
                            dur = 1
                        current_end_hour = int(event['time'].split(':')[0]) + dur
                        edit_end_time = st.selectbox("Till:", [f"{h:02d}:00" for h in range(7, 24)],
                                                    index=min(current_end_hour - 7, 17),
                                                    key=f"edit_end_{event['id']}")

                    edit_desc = st.text_area("Beskrivning:", value=event.get('description', ''),
                                            key=f"edit_desc_{event['id']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Spara", key=f"save_{event['id']}", use_container_width=True):
                            # Beräkna ny duration
                            start_hour = int(edit_time.split(':')[0])
                            end_hour = int(edit_end_time.split(':')[0])
                            new_duration = max(1, end_hour - start_hour)

                            # Uppdatera händelse
                            conn = sqlite3.connect('familjekalender.db')
                            c = conn.cursor()
                            c.execute('UPDATE events SET user=?, title=?, time=?, description=?, duration=? WHERE id=?',
                                    (edit_user, edit_title, edit_time, edit_desc, new_duration, event['id']))
                            conn.commit()
                            conn.close()
                            st.session_state.show_add_dialog = False
                            st.success("Händelse uppdaterad!")
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Ta bort", key=f"delete_{event['id']}", use_container_width=True):
                            # Kolla om det är en återkommande händelse
                            if event.get('repeat_pattern'):
                                # Visa val för återkommande händelser
                                st.warning("Detta är en återkommande händelse")
                                col_del1, col_del2 = st.columns(2)
                                with col_del1:
                                    if st.button("Ta bort endast denna", key=f"delete_single_{event['id']}", use_container_width=True):
                                        # Skapa undantag för detta datum genom att sätta repeat_until till dagen innan
                                        conn = sqlite3.connect('familjekalender.db')
                                        c = conn.cursor()
                                        current_date = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').date()
                                        # Sätt repeat_until till dagen innan detta datum
                                        new_until = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
                                        c.execute('UPDATE events SET repeat_until=? WHERE id=?', (new_until, event['id']))
                                        conn.commit()
                                        conn.close()
                                        st.session_state.show_add_dialog = False
                                        st.success("Denna förekomst borttagen!")
                                        st.rerun()
                                with col_del2:
                                    if st.button("Ta bort alla", key=f"delete_all_{event['id']}", use_container_width=True):
                                        delete_event(event['id'])
                                        st.session_state.show_add_dialog = False
                                        st.success("Alla förekomster borttagna!")
                                        st.rerun()
                            else:
                                # Vanlig händelse - ta bort direkt
                                delete_event(event['id'])
                                st.session_state.show_add_dialog = False
                                st.rerun()
            st.divider()

        st.subheader("➕ Lägg till ny händelse")

        event_user = st.selectbox("Vem:", ["Albin", "Maria", "Olle", "Ellen", "Familj"])
        event_title = st.text_input("Titel:", placeholder="T.ex. Läkarbesök, Träning...")

        col_start, col_end = st.columns(2)
        with col_start:
            event_time = st.selectbox("Från:", [f"{h:02d}:00" for h in range(7, 23)],
                                     index=[f"{h:02d}:00" for h in range(7, 23)].index(st.session_state.selected_time))
        with col_end:
            # Beräkna sluttid baserat på starttid (1 timme senare som default)
            start_hour = int(st.session_state.selected_time.split(':')[0])
            default_end_hour = min(start_hour + 1, 23)
            event_end_time = st.selectbox("Till:", [f"{h:02d}:00" for h in range(7, 24)],
                                         index=max(0, default_end_hour - 7))

        event_description = st.text_area("Beskrivning:", placeholder="Extra detaljer (frivilligt)")

        # Återkommande händelse
        st.markdown("#### 🔁 Upprepa händelse")
        repeat_enabled = st.checkbox("Upprepa varje vecka", value=False)

        repeat_pattern = None
        repeat_until = None

        if repeat_enabled:
            col_repeat_day, col_repeat_until = st.columns(2)
            with col_repeat_day:
                repeat_pattern = st.selectbox("Veckodag:", ["mån", "tis", "ons", "tor", "fre", "lör", "sön"])
            with col_repeat_until:
                # Default: 3 månader framåt
                default_until = datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').date() + timedelta(days=90)
                repeat_until_date = st.date_input("Upprepa till:", value=default_until)
                repeat_until = repeat_until_date.strftime('%Y-%m-%d')

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            if st.button("✨ Lägg till", use_container_width=True, type="primary"):
                if event_title:
                    # Beräkna duration från start och sluttid
                    start_hour = int(event_time.split(':')[0])
                    end_hour = int(event_end_time.split(':')[0])
                    duration = max(1, end_hour - start_hour)

                    add_event(event_user, st.session_state.selected_date, event_time, event_title, event_description, duration, repeat_pattern, repeat_until)
                    st.session_state.show_add_dialog = False
                    st.success(f"Händelse tillagd!")
                    st.rerun()
                else:
                    st.error("Titel måste anges")
        with col_cancel:
            if st.button("❌ Stäng", use_container_width=True):
                st.session_state.show_add_dialog = False
                st.rerun()

    if st.session_state.show_add_dialog:
        show_event_dialog()

    # Navigation i botten - veckonavigering (endast pilar)
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    nav_bottom_col1, nav_bottom_col2 = st.columns(2)

    with nav_bottom_col1:
        if st.button("⬅️", use_container_width=True, key="prev_week_bottom"):
            st.session_state['current_week'] -= timedelta(days=7)
            st.rerun()

    with nav_bottom_col2:
        if st.button("➡️", use_container_width=True, key="next_week_bottom"):
            st.session_state['current_week'] += timedelta(days=7)
            st.rerun()

if __name__ == "__main__":
    main()