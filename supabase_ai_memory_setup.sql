-- ============================================================
-- FAMILJEKALENDER AI-MINNE MED PGVECTOR
-- ============================================================
-- Detta skript skapar tabeller för AI långtidsminne
-- Kör detta i Supabase SQL Editor
-- ============================================================

-- Steg 1: Aktivera pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Steg 2: Skapa ai_memories tabell
CREATE TABLE IF NOT EXISTS ai_memories (
  id BIGSERIAL PRIMARY KEY,

  -- Vem pratade med AI:n
  user_name TEXT,  -- 'Albin', 'Maria', 'Olle', 'Ellen', 'Familj', eller NULL för allmänt

  -- Typ av interaktion
  conversation_type TEXT NOT NULL,  -- 'question', 'booking', 'preference', 'pattern', 'feedback'

  -- Konversationen
  user_message TEXT NOT NULL,
  ai_response TEXT NOT NULL,

  -- Vector embedding för semantisk sökning (1536 dimensioner för text-embedding-3-small)
  embedding VECTOR(1536),

  -- Metadata (JSON för flexibilitet)
  metadata JSONB DEFAULT '{}',
  -- Exempel metadata:
  -- {
  --   "event_id": 123,           -- Om relaterat till en händelse
  --   "date_mentioned": "2024-10-20",
  --   "time_mentioned": "12:00",
  --   "tags": ["lunch", "work"],
  --   "sentiment": "positive"
  -- }

  -- Relevans över tid (sjunker gradvis)
  relevance_score FLOAT DEFAULT 1.0,  -- 1.0 = nytt minne, sjunker över tid

  -- Tidsstämplar
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Steg 3: Skapa index för snabb sökning
-- IVFFlat index för vector similarity search (cosine similarity)
CREATE INDEX IF NOT EXISTS ai_memories_embedding_idx
  ON ai_memories
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

-- Index för filtrering
CREATE INDEX IF NOT EXISTS ai_memories_user_name_idx ON ai_memories (user_name);
CREATE INDEX IF NOT EXISTS ai_memories_conversation_type_idx ON ai_memories (conversation_type);
CREATE INDEX IF NOT EXISTS ai_memories_created_at_idx ON ai_memories (created_at DESC);
CREATE INDEX IF NOT EXISTS ai_memories_relevance_score_idx ON ai_memories (relevance_score DESC);

-- GIN index för JSONB metadata
CREATE INDEX IF NOT EXISTS ai_memories_metadata_idx ON ai_memories USING GIN (metadata);

-- Steg 4: Skapa tabell för användarpreferenser (lättare att söka)
CREATE TABLE IF NOT EXISTS user_preferences (
  id BIGSERIAL PRIMARY KEY,
  user_name TEXT NOT NULL,
  preference_key TEXT NOT NULL,  -- 'default_meeting_time', 'favorite_lunch_spot', etc.
  preference_value TEXT NOT NULL,
  confidence FLOAT DEFAULT 0.5,  -- Hur säker är AI:n (0-1)
  times_confirmed INT DEFAULT 1,  -- Antal gånger mönstret observerats
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_name, preference_key)
);

-- Index för preferenser
CREATE INDEX IF NOT EXISTS user_preferences_user_name_idx ON user_preferences (user_name);
CREATE INDEX IF NOT EXISTS user_preferences_confidence_idx ON user_preferences (confidence DESC);

-- Steg 5: Skapa funktion för att söka liknande minnen (semantisk sökning)
CREATE OR REPLACE FUNCTION search_similar_memories(
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 5,
  filter_user TEXT DEFAULT NULL
)
RETURNS TABLE (
  id BIGINT,
  user_name TEXT,
  conversation_type TEXT,
  user_message TEXT,
  ai_response TEXT,
  metadata JSONB,
  similarity FLOAT,
  created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ai_memories.id,
    ai_memories.user_name,
    ai_memories.conversation_type,
    ai_memories.user_message,
    ai_memories.ai_response,
    ai_memories.metadata,
    1 - (ai_memories.embedding <=> query_embedding) AS similarity,
    ai_memories.created_at
  FROM ai_memories
  WHERE
    (filter_user IS NULL OR ai_memories.user_name = filter_user)
    AND (1 - (ai_memories.embedding <=> query_embedding)) > match_threshold
  ORDER BY ai_memories.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Steg 6: Skapa funktion för att automatiskt minska relevans över tid
CREATE OR REPLACE FUNCTION decay_memory_relevance()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Minska relevans med 0.1% per dag för minnen äldre än 7 dagar
  UPDATE ai_memories
  SET relevance_score = GREATEST(0.1, relevance_score * 0.999)
  WHERE created_at < NOW() - INTERVAL '7 days'
    AND relevance_score > 0.1;
END;
$$;

-- Steg 7: Row Level Security (RLS) - Valfritt men rekommenderat
ALTER TABLE ai_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Tillåt alla operationer för authenticated users (eller anon för Streamlit)
CREATE POLICY "Allow all for anon" ON ai_memories FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON user_preferences FOR ALL USING (true);

-- Steg 8: Skapa vy för senaste relevanta minnen
CREATE OR REPLACE VIEW recent_relevant_memories AS
SELECT
  id,
  user_name,
  conversation_type,
  user_message,
  ai_response,
  metadata,
  relevance_score,
  created_at,
  EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400 AS days_old
FROM ai_memories
WHERE relevance_score > 0.3
ORDER BY
  relevance_score DESC,
  created_at DESC
LIMIT 100;

-- ============================================================
-- KLART! Nu har du:
-- ============================================================
-- ✅ ai_memories tabell med pgvector för semantisk sökning
-- ✅ user_preferences för lätta preferenser
-- ✅ search_similar_memories() funktion för att hitta relevanta minnen
-- ✅ Automatisk relevans-decay över tid
-- ✅ Index för snabb sökning
-- ✅ Row Level Security
--
-- NÄSTA STEG:
-- 1. Kör detta script i Supabase SQL Editor
-- 2. Implementera Python-kod för att spara/hämta minnen
-- 3. Integrera embeddings i AI-flödet
-- ============================================================
