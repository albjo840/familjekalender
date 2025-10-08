# Changelog - Familjekalender

## 2025-10-08 - Uppdateringar och buggfixar

### ✨ Nya funktioner

1. **Utökade bokningsbara tider (06:00-22:00)**
   - Tidigare: 07:00-22:00
   - Nu: 06:00-22:00
   - Möjlighet att boka tidigt på morgonen

2. **Minutprecision för tider**
   - Du kan nu välja exakta minuter vid bokning (t.ex. 16:50)
   - 5-minuters intervall i dropdown-menyer
   - Fungerar både vid ny bokning och redigering av händelser

3. **Påminnelsenotifikationer**
   - Ny checkbox: "🔔 Påminnelse 15 min innan"
   - Push-notifikationer via webbläsaren 15 minuter innan en händelse
   - Kräver notifikationspermission i webbläsaren
   - Fungerar även när appen inte är öppen (PWA)

4. **Smartare upprepade händelser**
   - Veckodagen beräknas automatiskt från valt datum
   - Ingen manuell veckodag-väljare längre
   - Tydlig info-box visar vilket datum och veckodag som upprepas

### 🐛 Buggfixar

1. **Fixat: Kan inte ta bort upprepade händelser**
   - Tidigare krävdes extra klick för att få upp borttagningsknapparna
   - Nu visas alternativen direkt när du klickar på en upprepning:
     - "Ta bort endast denna" - Tar bort bara den specifika förekomsten
     - "Ta bort alla" - Tar bort alla framtida förekomster
   - För vanliga händelser: Direkt borttagningsknapp

2. **Kronologisk sortering av händelser**
   - Händelser på samma dag sorteras nu automatiskt i tidsordning
   - Tidigt på dagen visas först, senare händelser längre ner
   - Bättre översikt över dagens schema

### 🔧 Tekniska förbättringar

1. **Förbättrad datapersistens**
   - Automatisk backup av databasen efter varje ändring
   - Återställning från backup vid appstart om databasen saknas
   - Miljövariabel `CALENDAR_DB_PATH` för att ställa in anpassad databasplats
   - Skydd mot dataförlust vid omstart av Streamlit-servern

2. **Ny databas-kolumn: `reminder`**
   - Boolean-fält för att markera händelser med påminnelser
   - Migrering sker automatiskt vid uppstart

### 📝 Dokumentation

- Uppdaterad `claude.md` med all ny funktionalitet
- Denna changelog-fil skapad för att spåra ändringar

## Installation av uppdateringarna

```bash
# 1. Hämta senaste koden
git pull

# 2. Starta om appen
streamlit run app.py
```

Databasen migreras automatiskt vid första start - inga manuella steg behövs!

## Notiser för pushnotifikationer

För att aktivera pushnotifikationer:

1. Öppna appen i din webbläsare
2. När du får frågan om notifikationspermission, klicka på "Tillåt"
3. Bocka i "🔔 Påminnelse 15 min innan" när du skapar en händelse
4. Du får automatiskt en notifikation 15 minuter innan händelsen

**OBS**: Fungerar bäst i Chrome/Edge och kräver att webbläsaren är öppen i bakgrunden.
