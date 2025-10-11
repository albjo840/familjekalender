import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import calendar
import requests
import json

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
            padding: 0 2px !important;
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
    conn.commit()
    conn.close()

def add_event(user, date, time, title, description="", duration=1):
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO events (user, date, time, title, description, duration)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user, date, time, title, description, duration))
    conn.commit()
    conn.close()

def update_event_duration(event_id, new_duration):
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()
    c.execute('UPDATE events SET duration = ? WHERE id = ?', (new_duration, event_id))
    conn.commit()
    conn.close()

def get_events_for_week(start_date):
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()

    end_date = start_date + timedelta(days=6)
    c.execute('''
        SELECT * FROM events
        WHERE date BETWEEN ? AND ?
        ORDER BY date, time
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))

    events = c.fetchall()
    conn.close()
    return events

def get_events_for_month(year, month):
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()

    # Första och sista dagen i månaden
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

    c.execute('''
        SELECT * FROM events
        WHERE date BETWEEN ? AND ?
        ORDER BY date, time
    ''', (first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

    events = c.fetchall()
    conn.close()
    return events

def delete_event(event_id):
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()
    c.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
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
            event_id, user, date, time, title, desc, duration, created = event
            context += f"- {date} kl {time}: {title} ({user})"
            if desc:
                context += f" - {desc}"
            if duration and int(duration) > 1:
                context += f" [{duration} timmar]"
            context += "\n"

    return context

def get_available_times(date_str, user=None):
    """Hittar lediga tider för ett givet datum"""
    conn = sqlite3.connect('familjekalender.db')
    c = conn.cursor()

    if user:
        c.execute('SELECT time, duration FROM events WHERE date = ? AND user = ? ORDER BY time',
                 (date_str, user))
    else:
        c.execute('SELECT time, duration FROM events WHERE date = ? ORDER BY time',
                 (date_str,))

    booked_events = c.fetchall()
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
def get_huggingface_api_key():
    """Hämtar Hugging Face API-nyckel från secrets eller session state"""
    # Försök från Streamlit secrets först
    if hasattr(st, 'secrets') and 'HUGGINGFACE_API_KEY' in st.secrets:
        return st.secrets['HUGGINGFACE_API_KEY']

    # Annars från session state (användaren kan mata in den)
    if 'hf_api_key' in st.session_state and st.session_state.hf_api_key:
        return st.session_state.hf_api_key

    return None

def call_gpt_local(user_message, year, month):
    """Anropar Hugging Face Inference API för AI-assistans"""

    # Hämta API-nyckel
    api_key = get_huggingface_api_key()

    if not api_key:
        return "⚠️ Ingen Hugging Face API-nyckel hittades. Lägg till din nyckel i .streamlit/secrets.toml eller mata in den i sidebaren."

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

    try:
        # Hugging Face Inference API endpoint
        API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"
        headers = {"Authorization": f"Bearer {api_key}"}

        # Skapa chat messages
        payload = {
            "inputs": f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n",
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }

        # Anropa API
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()

            # Extrahera svaret
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', '').strip()
            else:
                ai_response = result.get('generated_text', '').strip()

            # Ta bort eventuella specialtokens
            ai_response = ai_response.replace('<|im_end|>', '').replace('<|im_start|>', '').strip()

            # Kontrollera om AI:n vill boka en händelse
            if "BOOK_EVENT|" in ai_response:
                import re
                # Extrahera BOOK_EVENT-kommandot (ta bara första raden om det finns flera)
                book_line = ai_response.split("BOOK_EVENT|")[1].split("\n")[0]
                parts = book_line.split("|")

                if len(parts) >= 4:
                    user, date, time, title = parts[:4]
                    description = parts[4].strip() if len(parts) > 4 else ""

                    # Hantera duration säkert - ta bort allt efter första icke-siffran
                    duration = 1
                    if len(parts) > 5:
                        duration_str = parts[5].strip()
                        # Extrahera bara siffror från början av strängen
                        match = re.match(r'^\d+', duration_str)
                        if match:
                            duration = int(match.group())

                    booking_result = ai_book_event(user.strip(), date.strip(), time.strip(),
                                                   title.strip(), description, duration)

                    # Ta bort BOOK_EVENT-kommandot från svaret
                    ai_response = ai_response.split("BOOK_EVENT|")[0].strip() + "\n\n" + booking_result

            return ai_response

        elif response.status_code == 503:
            return "⏳ AI-modellen laddar... Försök igen om några sekunder."
        else:
            return f"⚠️ API-fel ({response.status_code}): {response.text}"

    except requests.Timeout:
        return "⏱️ Timeout - försök igen om ett ögonblick."
    except Exception as e:
        return f"⚠️ Fel vid AI-anrop: {str(e)}"

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

    # Röstinmatning med Web Speech API
    st.markdown("""
    <div id="voice-input-container" style="text-align: center; margin-bottom: 1rem;">
        <button id="voice-button" onclick="startVoiceRecognition()"
                style="background: linear-gradient(135deg, #ff3b30 0%, #ff6b6b 100%);
                       color: white; border: none; border-radius: 50%; width: 60px; height: 60px;
                       font-size: 24px; cursor: pointer; box-shadow: 0 4px 12px rgba(255,59,48,0.3);
                       transition: all 0.3s ease;">
            🎤
        </button>
        <p id="voice-status" style="color: white; margin-top: 0.5rem; font-size: 13px;"></p>
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
            button.style.background = 'linear-gradient(135deg, #ff3b30 0%, #ff6b6b 100%)';
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

            // Sätt input i Streamlit chat
            const chatInput = window.parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                chatInput.value = transcript;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        };

        recognition.onerror = function(event) {
            button.style.background = 'linear-gradient(135deg, #ff3b30 0%, #ff6b6b 100%)';
            button.textContent = '🎤';
            status.textContent = 'Fel: ' + event.error;
            isRecording = false;
        };

        recognition.onend = function() {
            button.style.background = 'linear-gradient(135deg, #ff3b30 0%, #ff6b6b 100%)';
            button.textContent = '🎤';
            isRecording = false;
        };

        recognition.start();
    }
    </script>
    """, unsafe_allow_html=True)

    # Chat input
    user_input = st.chat_input("Ställ en fråga om kalendern eller be mig boka något...")

    if user_input:
        # Anropa AI:n (lokalt på GPU)
        with st.spinner('🤔 Tänker...'):
            ai_response = call_gpt_local(user_input, st.session_state['current_year'], st.session_state['current_month'])

        # Visa svaret tillfälligt med auto-dismiss
        if "✓" in ai_response:  # Om bokning genomfördes
            st.success(ai_response)
            # Vänta 2 sekunder och uppdatera kalendern
            import time
            time.sleep(2)
            st.rerun()
        else:
            # Visa svar för frågor
            st.info(ai_response)

    # Navigation i toppen
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])

    with nav_col1:
        if st.button("⬅️ Föregående", use_container_width=True):
            if st.session_state['current_month'] == 1:
                st.session_state['current_month'] = 12
                st.session_state['current_year'] -= 1
            else:
                st.session_state['current_month'] -= 1
            st.rerun()

    with nav_col2:
        month_names = ['Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni',
                      'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December']
        st.markdown(f"""
        <div style='text-align:center;font-weight:600;font-size:1.5rem;color:white;padding:8px;
                    background:rgba(255,255,255,0.1);border-radius:12px;backdrop-filter:blur(10px);'>
            {month_names[st.session_state['current_month']-1]} {st.session_state['current_year']}
        </div>
        """, unsafe_allow_html=True)

    with nav_col3:
        if st.button("Nästa ➡️", use_container_width=True):
            if st.session_state['current_month'] == 12:
                st.session_state['current_month'] = 1
                st.session_state['current_year'] += 1
            else:
                st.session_state['current_month'] += 1
            st.rerun()


    # Hämta händelser för månaden
    events = get_events_for_month(st.session_state['current_year'], st.session_state['current_month'])

    # Skapa DataFrame för enklare hantering
    if events:
        # Databasen har 10 kolumner: id, user, date, time, duration, title, description, created_at, repeat_pattern, repeat_until
        num_cols = len(events[0])

        if num_cols >= 10:  # Full struktur med repeat
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'duration', 'title', 'description', 'created_at', 'repeat_pattern', 'repeat_until'])
        elif num_cols >= 8:  # Struktur med duration men utan repeat
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'duration', 'title', 'description', 'created_at'])
            events_df['repeat_pattern'] = None
            events_df['repeat_until'] = None
        else:  # Gammal struktur utan duration
            events_df = pd.DataFrame(events, columns=['id', 'user', 'date', 'time', 'title', 'description', 'created_at'])
            events_df['duration'] = 1  # Sätt default duration
            events_df['repeat_pattern'] = None
            events_df['repeat_until'] = None
    else:
        events_df = pd.DataFrame(columns=['id', 'user', 'date', 'time', 'duration', 'title', 'description', 'created_at', 'repeat_pattern', 'repeat_until'])

    # Dialog för att lägga till händelse
    if 'show_add_dialog' not in st.session_state:
        st.session_state.show_add_dialog = False
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_time' not in st.session_state:
        st.session_state.selected_time = None
    if 'existing_events' not in st.session_state:
        st.session_state.existing_events = []

    # Skapa månatlig kalendervy
    import calendar as cal

    # Få kalendergrid för månaden
    month_calendar = cal.monthcalendar(st.session_state['current_year'], st.session_state['current_month'])

    # Veckodagar
    weekdays = ['Mån', 'Tis', 'Ons', 'Tor', 'Fre', 'Lör', 'Sön']

    # Visa veckodagar som headers
    header_cols = st.columns(7)
    for idx, day in enumerate(weekdays):
        with header_cols[idx]:
            st.markdown(f'<div style="text-align:center;font-weight:600;color:white;padding:12px 0;background:rgba(255,255,255,0.1);border-radius:8px;margin:2px;">{day}</div>', unsafe_allow_html=True)

    # Visa varje vecka
    for week in month_calendar:
        week_cols = st.columns(7)

        for day_idx, day in enumerate(week):
            with week_cols[day_idx]:
                if day == 0:
                    # Tom dag (från föregående/nästa månad)
                    st.markdown('<div style="min-height:120px;background:rgba(255,255,255,0.05);border-radius:12px;margin:2px;"></div>', unsafe_allow_html=True)
                else:
                    # Skapa datum för denna dag
                    date_obj = datetime(st.session_state['current_year'], st.session_state['current_month'], day).date()
                    date_str = date_obj.strftime('%Y-%m-%d')

                    # Kolla om det är idag
                    is_today = date_obj == datetime.now().date()
                    today_style = "border:3px solid #4facfe;" if is_today else ""

                    # Hämta händelser för denna dag
                    day_events = events_df[events_df['date'] == date_str]

                    # Rita dagruta
                    events_html = ""
                    for _, event in day_events.iterrows():
                        user_class = f"user-{event['user'].lower()}"
                        events_html += f'<div class="event {user_class}" style="margin:4px 0;padding:4px 6px;border-radius:6px;font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{event["title"]}</div>'

                    st.markdown(f'''
                    <div style="min-height:120px;background:rgba(255,255,255,0.95);border-radius:12px;margin:2px;padding:8px;{today_style}box-shadow:0 4px 12px rgba(0,0,0,0.1);transition:transform 0.2s ease,box-shadow 0.2s ease;" onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 20px rgba(0,0,0,0.15)';" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)';">
                        <div style="font-weight:600;font-size:18px;color:#333;margin-bottom:8px;">{day}</div>
                        {events_html}
                    </div>
                    ''', unsafe_allow_html=True)

                    # Klickbar knapp
                    if st.button("➕", key=f"add_{date_str}", use_container_width=True):
                        st.session_state.show_add_dialog = True
                        st.session_state.selected_date = date_str
                        st.session_state.selected_time = "09:00"
                        existing = day_events.to_dict('records') if not day_events.empty else []
                        st.session_state.existing_events = existing
                        st.rerun()

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
                    edit_user = st.selectbox("Vem:", ["Albin", "Maria", "Familj"],
                                            index=["Albin", "Maria", "Familj"].index(event['user']),
                                            key=f"edit_user_{event['id']}")
                    edit_title = st.text_input("Titel:", value=event['title'], key=f"edit_title_{event['id']}")

                    col_e_start, col_e_end = st.columns(2)
                    with col_e_start:
                        edit_time = st.selectbox("Från:", [f"{h:02d}:00" for h in range(7, 23)],
                                                index=[f"{h:02d}:00" for h in range(7, 23)].index(event['time']),
                                                key=f"edit_time_{event['id']}")
                    with col_e_end:
                        current_duration = event.get('duration', 1)
                        current_end_hour = int(event['time'].split(':')[0]) + current_duration
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
                            delete_event(event['id'])
                            st.session_state.show_add_dialog = False
                            st.rerun()
            st.divider()

        st.subheader("➕ Lägg till ny händelse")

        event_user = st.selectbox("Vem:", ["Albin", "Maria", "Familj"])
        event_title = st.text_input("Titel:", placeholder="T.ex. Läkarbesök, Träning...")

        col_start, col_end = st.columns(2)
        with col_start:
            event_time = st.selectbox("Från:", [f"{h:02d}:00" for h in range(7, 23)],
                                     index=[f"{h:02d}:00" for h in range(7, 23)].index(st.session_state.selected_time))
        with col_end:
            event_end_time = st.selectbox("Till:", [f"{h:02d}:00" for h in range(7, 24)],
                                         index=min(1, 24 - int(st.session_state.selected_time.split(':')[0]) - 7))

        event_description = st.text_area("Beskrivning:", placeholder="Extra detaljer (frivilligt)")

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            if st.button("✨ Lägg till", use_container_width=True, type="primary"):
                if event_title:
                    # Beräkna duration från start och sluttid
                    start_hour = int(event_time.split(':')[0])
                    end_hour = int(event_end_time.split(':')[0])
                    duration = max(1, end_hour - start_hour)

                    add_event(event_user, st.session_state.selected_date, event_time, event_title, event_description, duration)
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

    # Visa alla händelser för veckan i en lista (för backup/översikt)
    if not events_df.empty:
        st.header("📋 Alla händelser denna vecka")

        # Gruppera efter användare
        for user in ['Albin', 'Maria', 'Familj']:
            user_events = events_df[events_df['user'] == user]
            if not user_events.empty:
                st.subheader(f"{user}s händelser")
                for _, event in user_events.iterrows():
                    date_obj = datetime.strptime(event['date'], '%Y-%m-%d').date()
                    day_name = calendar.day_name[date_obj.weekday()]

                    col1, col2, col3 = st.columns([2, 4, 1])
                    with col1:
                        st.write(f"**{day_name} {event['time']}**")
                    with col2:
                        st.write(f"{event['title']}")
                        if event['description']:
                            st.write(f"*{event['description']}*")
                    with col3:
                        if st.button("🗑️", key=f"list_delete_{event['id']}"):
                            delete_event(event['id'])
                            st.rerun()

if __name__ == "__main__":
    main()