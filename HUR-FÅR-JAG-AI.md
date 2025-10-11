# 🤖 Aktivera AI-assistenten (100% GRATIS)

Din familjekalender använder nu **Qwen 2.5 72B Instruct** - en av de bästa gratis AI-modellerna via Hugging Face.

## ⚡ Snabbstart (5 minuter)

### Steg 1: Skapa Hugging Face-konto (gratis)
1. Gå till: https://huggingface.co/join
2. Registrera med email eller Google
3. Bekräfta din email

### Steg 2: Skapa API-nyckel
1. Logga in på Hugging Face
2. Gå till: https://huggingface.co/settings/tokens
3. Klicka "New token"
4. Ge den ett namn (t.ex. "familjekalender")
5. Välj typ: **Read** (räcker för Inference API)
6. Klicka "Generate token"
7. **Kopiera nyckeln** (börjar med `hf_...`)

### Steg 3: Lägg till nyckeln i kalendern
1. Öppna projektet: `/home/albin/familjekalender`
2. Gå till mappen `.streamlit/`
3. Kopiera filen `secrets.toml.example` till `secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
4. Öppna `secrets.toml` och klistra in din nyckel:
   ```toml
   HUGGINGFACE_API_KEY = "hf_din_riktiga_nyckel_här"
   ```
5. Spara filen

### Steg 4: Starta kalendern
```bash
cd ~/familjekalender
streamlit run app.py
```

## ✅ Testa AI:n

När kalendern är igång, testa AI-assistenten med:

- **Frågor**:
  - "Vad har Albin bokat nästa vecka?"
  - "När är Maria ledig på fredag?"
  - "Vad finns bokat imorgon?"

- **Bokningar**:
  - "Boka lunch för Maria imorgon kl 12"
  - "Lägg till tandläkare för Albin på fredag 14:00"
  - "Skapa familjemiddag på lördag 18:00 i 2 timmar"

## 🌟 Fördelar med Qwen 2.5 72B

- ✅ **100% Gratis** - Ingen betalning krävs
- ✅ **Kraftfull** - 72 miljarder parametrar
- ✅ **Bra på svenska** - Förstår svensk text perfekt
- ✅ **Snabb** - Svarar på sekunder
- ✅ **Fungerar överallt** - Desktop, mobil, tablet
- ✅ **Ingen GPU krävs** - Körs i molnet via Hugging Face

## 🔒 Säkerhet

- Din API-nyckel lagras lokalt i `.streamlit/secrets.toml`
- Filen är redan i `.gitignore` så den pushas INTE till GitHub
- Dela ALDRIG din API-nyckel med någon

## ❓ Felsökning

### "Ingen Hugging Face API-nyckel hittades"
- Kontrollera att filen heter exakt `secrets.toml` (inte `.example`)
- Kontrollera att nyckeln börjar med `hf_`
- Starta om Streamlit-appen

### "AI-modellen laddar..."
- Första gången kan det ta 10-30 sekunder
- Vänta och försök igen

### "API-fel (401)"
- Din API-nyckel är ogiltig
- Skapa en ny på https://huggingface.co/settings/tokens

## 📱 Använda på mobilen

När din API-nyckel är konfigurerad fungerar AI:n automatiskt även på mobil när du öppnar kalendern i din mobilwebbläsare!

---

**Lycka till!** 🚀

Vid problem, läs huvuddokumentationen i `claude.md`
