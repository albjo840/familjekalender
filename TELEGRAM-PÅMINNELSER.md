# 📱 Telegram-påminnelser - Setup Guide

Din familjekalender kan nu skicka påminnelser direkt till dina telefoner via Telegram!

## 🚀 Snabbstart (10 minuter)

### Steg 1: Skapa Telegram Bot
1. Öppna Telegram på din telefon
2. Sök efter **@BotFather**
3. Skicka `/newbot`
4. Ge boten ett namn (t.ex. "Familjekalender Bot")
5. Ge boten ett användarnamn (måste sluta på "bot", t.ex. "taborsen_kalender_bot")
6. **Kopiera API-token** som du får (ser ut som: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Steg 2: Få ditt Chat ID
1. Sök efter **@userinfobot** på Telegram
2. Starta en konversation
3. **Kopiera ditt Chat ID** (ett nummer som: `123456789`)

### Steg 3: Lägg till i secrets.toml
```toml
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID_ALBIN = "123456789"
TELEGRAM_CHAT_ID_MARIA = "987654321"
```

### Steg 4: Testa!
1. Boka en händelse med påminnelse aktiverad
2. Du kommer få en Telegram-notis 15 minuter innan

## 🔔 Hur det fungerar

När du skapar en händelse och bockar i "🔔 Påminnelse 15 min innan":
1. Händelsen sparas med `reminder=True` i databasen
2. Ett background-jobb kollar varje minut efter kommande händelser
3. 15 minuter innan händelsen skickas en Telegram-notis
4. Notisen innehåller: titel, tid, och vem händelsen gäller

## 💡 Fördelar med Telegram

- ✅ **100% Gratis** - Inga kostnader
- ✅ **Fungerar överallt** - iOS, Android, Desktop
- ✅ **Pålitligt** - Notiser kommer även när appen är stängd
- ✅ **Ingen installation** - Telegram finns redan
- ✅ **Obegränsat** - Ingen gräns för antal notiser
- ✅ **Privat** - Ingen data delas med tredje part

## 🔧 Avancerad konfiguration

### Lägg till fler familjemedlemmar
```toml
TELEGRAM_CHAT_ID_OLLE = "111222333"
TELEGRAM_CHAT_ID_ELLEN = "444555666"
```

### Anpassa påminnelsetid
I koden kan du ändra från 15 minuter till valfri tid:
```python
reminder_minutes = 15  # Ändra här
```

### Schemalägg flera påminnelser
```python
# Skicka påminnelse 1 dag innan + 15 min innan
reminders = [1440, 15]  # minuter
```

## 🐛 Felsökning

### "Bot token ogiltig"
- Kontrollera att du kopierat hela token från BotFather
- Token ska börja med siffror följt av kolon och bokstäver

### "Chat ID fungerar inte"
- Starta en konversation med din bot först (sök efter bot-namnet)
- Skicka `/start` till boten
- Försök få Chat ID igen från @userinfobot

### "Får inga notiser"
1. Kontrollera att secrets.toml har rätt värden
2. Verifiera att händelsen har `reminder=True`
3. Kolla att tiden är minst 15 minuter i framtiden
4. Starta om Streamlit-appen

## 📝 Exempel på notis

```
📅 Påminnelse: Tandläkare

🕐 Börjar om 15 minuter (14:00)
👤 Albin

God förberedelse! 🙂
```

## 🔐 Säkerhet

- Token och Chat ID:n lagras lokalt i `secrets.toml`
- Filen är i `.gitignore` - pushas INTE till GitHub
- Endast du och dina familjemedlemmar får notiser
- Telegram är end-to-end krypterat

## 🆘 Support

Problem? Kontakta:
- Telegram Support: https://telegram.org/support
- BotFather för bot-frågor: @BotFather
- Familjekalender GitHub: https://github.com/albjo840/familjekalender

---

**Lycka till!** 🎉

Nu får ni aldrig missa en händelse igen!
