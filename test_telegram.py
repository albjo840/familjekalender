#!/usr/bin/env python3
"""
Test Telegram bot connection
"""
import requests

TELEGRAM_BOT_TOKEN = "***REMOVED***"
TELEGRAM_CHAT_ID_ALBIN = "***REMOVED***"
TELEGRAM_CHAT_ID_MARIA = "***REMOVED***"

print("=" * 60)
print("TELEGRAM BOT TEST")
print("=" * 60)

def send_telegram_message(bot_token, chat_id, message, user_name):
    """Skickar ett Telegram-meddelande"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print(f"✅ Meddelande skickat till {user_name}!")
            return True
        else:
            print(f"❌ Fel vid skickning till {user_name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception för {user_name}: {e}")
        return False

# Testa bot info
try:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        bot_info = response.json()
        print(f"\n🤖 Bot info:")
        print(f"   Namn: {bot_info['result']['first_name']}")
        print(f"   Username: @{bot_info['result']['username']}")
        print(f"   ID: {bot_info['result']['id']}")
    else:
        print(f"❌ Kunde inte hämta bot info: {response.status_code}")
except Exception as e:
    print(f"❌ Fel vid hämtning av bot info: {e}")

# Skicka testmeddelande
print("\n📤 Skickar testmeddelanden...")

test_message = """🧪 *TEST-MEDDELANDE*

Detta är ett test av påminnelsesystemet.

Om du ser detta meddelande fungerar Telegram-boten korrekt! ✅

/Familjekalender Bot"""

send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_ALBIN, test_message, "Albin")
send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID_MARIA, test_message, "Maria")

print("\n✅ Test klart! Kolla dina Telegram-appar.")
