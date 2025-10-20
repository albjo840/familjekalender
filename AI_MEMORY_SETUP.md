# 🧠 AI Långtidsminne Setup Guide

Detta guide hjälper dig att aktivera AI-minnesystemet med pgvector i Supabase.

## Vad ger AI-minne dig?

✅ **Långtidsminne** - AI:n kommer ihåg tidigare konversationer
✅ **Semantisk sökning** - Hittar relevanta minnen baserat på sammanhang
✅ **Personliga preferenser** - Lär sig familjemedlemmars vanor
✅ **Smarta förslag** - "Du brukar boka lunch kl 12, vill du göra det nu?"
✅ **Konversationshistorik** - "Vad sa jag om mötet igår?"

---

## Steg 1: Kör SQL-migrationen i Supabase

1. **Öppna Supabase Dashboard**: https://supabase.com/dashboard
2. **Välj ditt projekt** (samma som du använder för kalendern)
3. **Gå till SQL Editor** (vänster meny)
4. **Skapa en ny query**
5. **Kopiera innehållet från** `supabase_ai_memory_setup.sql`
6. **Kör scriptet** (klicka "Run" eller Ctrl+Enter)

### Vad skapas?

- ✅ `ai_memories` tabell med pgvector för semantisk sökning
- ✅ `user_preferences` tabell för användarpreferenser
- ✅ `search_similar_memories()` funktion för att hitta relevanta minnen
- ✅ Index för snabb sökning
- ✅ Row Level Security (RLS)

---

## Steg 2: Verifiera att pgvector fungerar

I Supabase SQL Editor, kör:

```sql
-- Kontrollera att pgvector extension är aktiverad
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Kontrollera att tabellerna skapades
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('ai_memories', 'user_preferences');

-- Testa att spara ett minne (testdata)
INSERT INTO ai_memories (
  user_name,
  conversation_type,
  user_message,
  ai_response,
  embedding,
  metadata
) VALUES (
  'Albin',
  'question',
  'Vad gör jag imorgon?',
  'Du har ett möte kl 9:00',
  ARRAY(SELECT random() FROM generate_series(1, 1536))::vector,  -- Dummy embedding
  '{"test": true}'::jsonb
);

-- Verifiera att det funkade
SELECT COUNT(*) FROM ai_memories;
```

Om du ser `1` så fungerar allt! 🎉

---

## Steg 3: Aktivera i Streamlit Cloud (KLART!)

Koden är redan integrerad! AI-minnet aktiveras automatiskt om du har:

- ✅ `GROQ_API_KEY` i Streamlit secrets
- ✅ `SUPABASE_URL` i Streamlit secrets
- ✅ `SUPABASE_KEY` i Streamlit secrets

**Inget mer behövs!** Systemet börjar spara minnen direkt.

---

## Hur AI-minnet fungerar

### 1. Automatisk minneslagring

Varje gång någon pratar med AI:n sparas konversationen:

```python
# Exempel: Användaren frågar
"Vad gör Albin den 17e?"

# AI svarar
"Albin har möte kl 9:00 och lunch kl 12:00"

# Systemet sparar automatiskt:
- user_message: "Vad gör Albin den 17e?"
- ai_response: "Albin har möte kl 9:00..."
- conversation_type: "question"
- embedding: [0.123, 0.456, ...] (1536 floats)
- metadata: {"date_mentioned": "2024-10-17"}
```

### 2. Semantisk sökning vid nästa fråga

Nästa gång användaren frågar något liknande:

```python
# Användaren frågar
"Vad sa du om Albins schema?"

# Systemet:
1. Skapar embedding av frågan
2. Söker liknande minnen i databasen
3. Hittar föregående konversation (75% likhet)
4. Lägger till som kontext till AI:n

# AI:ns prompt får nu:
"""
🧠 LÅNGTIDSMINNE:
RELEVANTA TIDIGARE KONVERSATIONER:
  1. [75% likhet] Användare frågade: "Vad gör Albin den 17e?..."
"""

# AI kan nu svara med kontext:
"Som jag nämnde tidigare har Albin möte kl 9:00 och lunch kl 12:00 den 17e"
```

### 3. Personliga preferenser

AI:n kan lära sig mönster:

```python
# Efter flera bokningar:
"Boka lunch för Maria kl 12"  (3 gånger)
"Boka lunch för Maria kl 12"  (4 gånger)

# Systemet sparar preferens:
user_preferences:
  user_name: "Maria"
  preference_key: "default_lunch_time"
  preference_value: "12:00"
  confidence: 0.8
  times_confirmed: 4

# Nästa gång:
Användare: "Boka lunch för Maria imorgon"
AI: "Bokar lunch kl 12:00 (din vanliga tid). OK?"
```

---

## Användningsexempel

### Exempel 1: Konversationshistorik

```
Användare: "Boka lunch med Johan imorgon kl 12"
AI: "✅ Lunch med Johan bokad för 2024-10-21 kl 12:00"

[Nästa dag]
Användare: "Vad sa jag om lunch igår?"
AI: "Du bokade lunch med Johan för idag kl 12:00"
```

### Exempel 2: Personliga mönster

```
[Efter 5 bokningar på fredagskvällar]
Användare: "Är fredag ledig?"
AI: "Jag ser att du brukar hålla fredagskvällar lediga. Just nu är fredag helt ledig."
```

### Exempel 3: Smarta förslag

```
Användare: "Vad gör jag på måndag?"
AI: "Du har möte kl 9:00. Jag ser att du brukar boka lunch kl 12 på måndagar - vill du att jag lägger till det?"
```

---

## Prestanda och kostnader

### Embeddings

För nu används en enkel hash-baserad embedding (gratis men begränsad).

**För produktion (rekommenderat):**
1. Lägg till `OPENAI_API_KEY` i Streamlit secrets
2. Använd `text-embedding-3-small` modellen
3. Kostnad: ~$0.02 per 1M tokens (extremt billigt!)
4. Bättre semantisk förståelse

### Datalagring

- **Varje minne:** ~2-3 KB (text + embedding)
- **1000 konversationer:** ~2-3 MB
- **Supabase gratis tier:** 500 MB (rymmer ~150,000 konversationer!)

### Sökhastighet

- **pgvector med IVFFlat index:** <10ms per sökning
- **Typisk AI-respons:** ~500ms (varav bara ~10ms är minnesökning)

---

## Underhåll

### Automatisk relevans-decay

Gamla minnen får gradvis lägre relevans:

```sql
-- Kör månadsvis för att rensa gamla minnen
SELECT decay_memory_relevance();
```

Detta kan schemaläggas med Supabase Edge Functions.

### Manuell rensning

```sql
-- Ta bort minnen äldre än 6 månader med låg relevans
DELETE FROM ai_memories
WHERE created_at < NOW() - INTERVAL '6 months'
  AND relevance_score < 0.3;
```

---

## Felsökning

### AI:n kommer inte ihåg något

1. **Kontrollera att tabellerna finns:**
   ```sql
   SELECT COUNT(*) FROM ai_memories;
   ```

2. **Kontrollera Streamlit logs:**
   ```
   ✅ Konversation sparad till långtidsminne  <- Ska synas
   ```

3. **Kontrollera secrets:**
   - GROQ_API_KEY finns
   - SUPABASE_URL finns
   - SUPABASE_KEY finns

### Fel vid sökning

```sql
-- Kontrollera att search-funktionen finns
SELECT routine_name FROM information_schema.routines
WHERE routine_name = 'search_similar_memories';
```

### Prestanda-problem

```sql
-- Kontrollera index
SELECT indexname FROM pg_indexes
WHERE tablename = 'ai_memories';

-- Bör visa:
-- ai_memories_embedding_idx
-- ai_memories_user_name_idx
-- ai_memories_created_at_idx
```

---

## Nästa steg

Efter setup kan du:

1. **Testa minnesfunktionen** - Prata med AI:n, ställ samma fråga dagen efter
2. **Utforska preferenser** - Boka liknande händelser flera gånger
3. **Analysera minnen** - Använd Supabase Dashboard för att se sparade konversationer
4. **Optimera embeddings** - Lägg till OpenAI för bättre semantisk förståelse

---

## Support

Om något inte fungerar:
1. Kontrollera Supabase logs
2. Kontrollera Streamlit logs (Settings → Logs)
3. Verifiera SQL-skriptet kördes korrekt

**Allt klart!** 🎉 Nu har din AI långtidsminne och blir smartare för varje konversation!
