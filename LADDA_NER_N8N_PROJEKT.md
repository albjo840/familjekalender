# 📦 Ladda ner n8n-automations projektet

Ditt kompletta n8n-automations projekt är nu paketerat och redo att laddas ner!

## 📁 Tillgängliga filer

Du har två alternativ (samma innehåll):

- **n8n-automations.tar.gz** (143 KB) - för Linux/Mac
- **n8n-automations.zip** (59 KB) - för Windows eller om du föredrar zip

Båda filerna ligger i `/home/user/familjekalender/`

## 🚀 Instruktioner för nedladdning och push

### Steg 1: Ladda ner projektet

**Om du är på samma server:**
```bash
cd ~
cp /home/user/familjekalender/n8n-automations.tar.gz .
```

**Om du är på en annan dator:**
```bash
# Via scp (ändra till din server-adress)
scp user@taborsen.duckdns.org:/home/user/familjekalender/n8n-automations.tar.gz ~/
```

### Steg 2: Extrahera filerna

**För .tar.gz:**
```bash
cd ~
tar -xzf n8n-automations.tar.gz
cd n8n-automations
ls -la  # Du ska se saljrobot/, _template/, PITCH-filer, etc.
```

**För .zip:**
```bash
cd ~
unzip n8n-automations.zip
cd n8n-automations
```

### Steg 3: Verifiera innehållet

Kolla att du har allt:
```bash
ls -la

# Du ska se:
# - saljrobot/                    (din säljrobot)
# - _template/                    (mall för nya projekt)
# - PITCH_SALJCHEF.md            (business pitch)
# - PITCH_SAMMANFATTNING.md      (executive summary)
# - README.md                     (dokumentation)
# - deploy-to-server.sh          (deploy-script)
# - create-project.sh            (skapa nya projekt)
# och mer...
```

### Steg 4: Konfigurera Git remote

```bash
cd ~/n8n-automations
git remote -v  # Kolla om origin redan finns

# Om origin inte finns, lägg till den:
git remote add origin https://github.com/albjo840/n8n-automations.git

# Om du får "remote origin already exists", hoppa över ovan
```

### Steg 5: Pusha till GitHub

```bash
git push -u origin main --force
```

**När git frågar:**
- **Username:** `albjo840`
- **Password:** Din Personal Access Token (börjar med `ghp_...`)

**⚠️ VIKTIGT:** När du klistrar in token syns INGENTING - det är normalt! Tryck bara Enter när du klistrat in.

### Steg 6: Verifiera på GitHub

Gå till: **https://github.com/albjo840/n8n-automations**

Du ska nu se:
- ✅ saljrobot/ mappen med workflows
- ✅ _template/ för nya projekt
- ✅ PITCH_SALJCHEF.md
- ✅ PITCH_SAMMANFATTNING.md
- ✅ Alla deploy-scripts
- ✅ Komplett dokumentation

## 🔑 Om du inte har Personal Access Token

1. Gå till: https://github.com/settings/tokens
2. Klicka "Generate new token (classic)"
3. Note: `n8n-automations`
4. Kryssa i: **repo** (full repository access)
5. Klicka "Generate token"
6. **Kopiera token DIREKT** - du kan bara se den EN gång!

## 🎉 Klart!

När allt är uppladdat kan du börja använda projektet på din hemserver:

```bash
# På din hemserver:
cd ~/n8n-automations
./deploy-to-server.sh
# Välj "saljrobot"
```

Lycka till! 🚀
