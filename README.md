# 📅 Familjekalender

En gemensam kalender-app byggd med Streamlit för dig och din fru.

## Funktioner

- **Veckovy**: Måndag-Söndag, 07:00-22:00
- **Två användare**: Albin och Fru
- **Lägg till händelser**: Enkelt formulär för att skapa nya händelser
- **Redigera/Ta bort**: Enkla knappar för att hantera händelser
- **Färgkodning**: Olika färger för olika användare
- **Veckonavigation**: Enkelt att byta mellan veckor
- **Lokal databas**: SQLite för att spara alla händelser

## Kom igång

1. **Installera beroenden:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Kör appen:**
   ```bash
   streamlit run app.py
   ```

3. **Öppna i webbläsare:**
   - Appen öppnas automatiskt på `http://localhost:8501`
   - Båda kan använda samma URL för att komma åt kalendern

## Användning

1. **Välj användare** i sidomenyn (Albin eller Fru)
2. **Navigera mellan veckor** med pilknapparna eller datumväljaren
3. **Lägg till händelser** genom formuläret i sidomenyn
4. **Ta bort händelser** med 🗑️-knappen vid varje händelse
5. **Se översikt** av alla händelser längst ner på sidan

## Teknisk information

- **Frontend**: Streamlit
- **Databas**: SQLite (lokal fil: `familjekalender.db`)
- **Språk**: Python 3.7+
- **Port**: 8501 (standard för Streamlit)

## Tips

- **Nätverksåtkomst**: För att din fru ska kunna komma åt kalendern från sin dator, kör med:
  ```bash
  streamlit run app.py --server.address 0.0.0.0
  ```
  Sedan kan hon använda din dators IP-adress: `http://DIN-IP:8501`

- **Automatisk uppdatering**: Appen uppdateras automatiskt när någon lägger till eller tar bort händelser