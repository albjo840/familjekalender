#!/usr/bin/env python3
"""
Test AI-Assistent
=================
Testar Hugging Face AI-integration
"""

import streamlit as st
import requests
from datetime import datetime

print("="*60)
print("🤖 Testar AI-Assistent (Qwen 2.5 72B)...")
print("="*60)

# Hämta API-nyckel
try:
    hf_token = st.secrets.get("HUGGINGFACE_API_KEY", "")
except:
    hf_token = ""

if not hf_token:
    print("❌ HUGGINGFACE_API_KEY saknas i secrets")
    exit(1)

print(f"✅ API-nyckel hittad: {hf_token[:20]}...")

# Test 1: Enkel fråga
print("\n" + "="*60)
print("Test 1: Enkel fråga till AI")
print("="*60)

API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"
headers = {"Authorization": f"Bearer {hf_token}"}

system_message = """Du är en kalenderassistent på svenska.
Svara kort och trevligt på svenska."""

user_message = "Hej! Kan du svara på svenska?"

prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant\n"

payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "return_full_text": False
    }
}

print(f"📤 Skickar: '{user_message}'")
print("⏳ Väntar på svar...")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            ai_response = result[0].get('generated_text', '').strip()
        elif isinstance(result, dict):
            ai_response = result.get('generated_text', '').strip()
        else:
            ai_response = str(result)

        # Ta bort special tokens
        ai_response = ai_response.replace('<|im_end|>', '').replace('<|im_start|>', '').strip()

        print(f"\n✅ AI svarade:")
        print(f"   {ai_response}")

    elif response.status_code == 503:
        print("⚠️  Modellen håller på att ladda (503 Service Unavailable)")
        print("   Detta är normalt första gången - prova igen om 20 sekunder")
    else:
        print(f"❌ Fel: Status {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Fel vid anrop: {e}")

# Test 2: Kalenderfråga
print("\n" + "="*60)
print("Test 2: Kalenderfråga med kontext")
print("="*60)

today = datetime.now()
calendar_context = """
AKTUELLA HÄNDELSER:
- 2025-10-06 16:50: Olle - Blåskul (Musiklektion)
- 2025-10-06 17:00: Olle - Handbollsträning
- 2025-10-13 09:00: Olle - Innebandy
- 2025-11-03 17:00: Ellen - Fotbollsträning
"""

system_message_calendar = f"""Du är en kalenderassistent.

DAGENS DATUM: {today.strftime('%Y-%m-%d')}

KALENDER:
{calendar_context}

Svara kort på svenska om vad som finns bokat."""

user_message_calendar = "Vad har Olle bokat?"

prompt = f"<|im_start|>system\n{system_message_calendar}<|im_end|>\n<|im_start|>user\n{user_message_calendar}<|im_end|>\n<|im_start|>assistant\n"

payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 200,
        "temperature": 0.7,
        "top_p": 0.9,
        "return_full_text": False
    }
}

print(f"📤 Skickar: '{user_message_calendar}'")
print("⏳ Väntar på svar...")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            ai_response = result[0].get('generated_text', '').strip()
        elif isinstance(result, dict):
            ai_response = result.get('generated_text', '').strip()
        else:
            ai_response = str(result)

        ai_response = ai_response.replace('<|im_end|>', '').replace('<|im_start|>', '').strip()

        print(f"\n✅ AI svarade:")
        print(f"   {ai_response}")

    elif response.status_code == 503:
        print("⚠️  Modellen håller på att ladda (503 Service Unavailable)")
        print("   Prova igen om 20 sekunder")
    else:
        print(f"❌ Fel: Status {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Fel vid anrop: {e}")

print("\n" + "="*60)
print("✅ AI-test klart!")
print("="*60)
print("\n💡 Om du fick 503-fel första gången:")
print("   - Detta är normalt när modellen inte använts på ett tag")
print("   - Vänta 20-30 sekunder och kör: python3 test_ai.py igen")
print("   - Modellen kommer då vara redo och svara snabbt")
