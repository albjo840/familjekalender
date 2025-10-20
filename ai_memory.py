"""
AI Memory System för Familjekalender
Hanterar långtidsminne med pgvector i Supabase
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
import json

class AIMemory:
    """Hanterar AI-minnen med pgvector i Supabase"""

    def __init__(self, supabase_url: str, supabase_key: str, groq_api_key: str):
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.groq_api_key = groq_api_key
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generera embedding för text med hjälp av Groq
        Använder Llama 3.3 70B's text representation
        """
        try:
            # För produktionsmiljö skulle vi använda en dedikerad embedding-modell
            # Men vi kan också extrahera embeddings från Llama's representation
            # Alternativt: använd OpenAI text-embedding-3-small (billigt)

            # TILLFÄLLIG LÖSNING: Använd OpenAI för embeddings (extremt billigt)
            # Detta kan ersättas med lokal embedding-modell senare
            return self._generate_openai_embedding(text)

        except Exception as e:
            print(f"Embedding-fel: {e}")
            # Fallback: returnera dummy embedding (1536 dimensioner)
            return [0.0] * 1536

    def _generate_openai_embedding(self, text: str) -> List[float]:
        """
        Generera embedding med OpenAI (text-embedding-3-small)
        Kostar ~$0.02 per 1M tokens (extremt billigt)

        OBS: Detta kräver OPENAI_API_KEY i secrets.
        För nu returnerar vi en enkel hash-baserad embedding.
        """
        # TODO: Implementera OpenAI embeddings när användaren lägger till nyckel
        # För nu: använd en enkel hash-baserad representation
        return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> List[float]:
        """
        Enkel hash-baserad embedding för prototyping
        I produktion: byt till OpenAI text-embedding-3-small
        """
        import hashlib

        # Skapa en deterministisk embedding från text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        # Konvertera till 1536 floats (expandera hash)
        embedding = []
        for i in range(1536):
            byte_idx = i % len(hash_bytes)
            embedding.append((hash_bytes[byte_idx] / 255.0) - 0.5)

        # Normalisera
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def save_memory(
        self,
        user_message: str,
        ai_response: str,
        user_name: Optional[str] = None,
        conversation_type: str = "question",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Spara en konversation till AI-minnet

        Args:
            user_message: Vad användaren sa
            ai_response: AI:ns svar
            user_name: Vem som pratade (Albin, Maria, etc)
            conversation_type: 'question', 'booking', 'preference', 'pattern', 'feedback'
            metadata: Extra information (event_id, datum, etc)

        Returns:
            bool: True om lyckat
        """
        try:
            # Generera embedding för semantisk sökning
            combined_text = f"{user_message}\n{ai_response}"
            embedding = self.generate_embedding(combined_text)

            # Förbered data
            memory_data = {
                "user_name": user_name,
                "conversation_type": conversation_type,
                "user_message": user_message,
                "ai_response": ai_response,
                "embedding": embedding,
                "metadata": metadata or {},
                "relevance_score": 1.0
            }

            # Spara till Supabase
            url = f"{self.supabase_url}/rest/v1/ai_memories"
            response = requests.post(url, headers=self.headers, json=memory_data)

            if response.status_code in [200, 201]:
                print(f"✅ Minne sparat: {user_message[:50]}...")
                return True
            else:
                print(f"❌ Kunde inte spara minne: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Fel vid sparande av minne: {e}")
            return False

    def search_similar_memories(
        self,
        query: str,
        user_name: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Sök efter liknande minnen med semantisk sökning

        Args:
            query: Sökfråga
            user_name: Filtrera på specifik användare
            limit: Max antal resultat
            threshold: Minimipoäng för likhet (0-1)

        Returns:
            Lista med liknande minnen
        """
        try:
            # Generera embedding för sökning
            query_embedding = self.generate_embedding(query)

            # Anropa Supabase RPC-funktion
            url = f"{self.supabase_url}/rest/v1/rpc/search_similar_memories"
            payload = {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit,
                "filter_user": user_name
            }

            response = requests.post(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                results = response.json()
                print(f"🔍 Hittade {len(results)} liknande minnen")
                return results
            else:
                print(f"❌ Sökning misslyckades: {response.status_code}")
                return []

        except Exception as e:
            print(f"Fel vid sökning: {e}")
            return []

    def get_recent_memories(
        self,
        user_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Hämta senaste minnena

        Args:
            user_name: Filtrera på specifik användare
            limit: Max antal resultat

        Returns:
            Lista med senaste minnen
        """
        try:
            url = f"{self.supabase_url}/rest/v1/ai_memories"
            params = {
                "select": "*",
                "order": "created_at.desc",
                "limit": limit
            }

            if user_name:
                params["user_name"] = f"eq.{user_name}"

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception as e:
            print(f"Fel vid hämtning av minnen: {e}")
            return []

    def save_preference(
        self,
        user_name: str,
        preference_key: str,
        preference_value: str,
        confidence: float = 0.5
    ) -> bool:
        """
        Spara användarpreferens

        Args:
            user_name: Vem preferensen gäller
            preference_key: Typ av preferens (t.ex. 'default_meeting_time')
            preference_value: Värde (t.ex. '09:00')
            confidence: Hur säker är AI:n (0-1)

        Returns:
            bool: True om lyckat
        """
        try:
            url = f"{self.supabase_url}/rest/v1/user_preferences"
            data = {
                "user_name": user_name,
                "preference_key": preference_key,
                "preference_value": preference_value,
                "confidence": confidence,
                "times_confirmed": 1
            }

            # Upsert (uppdatera eller skapa)
            headers = {**self.headers, "Prefer": "resolution=merge-duplicates"}
            response = requests.post(url, headers=headers, json=data)

            return response.status_code in [200, 201]

        except Exception as e:
            print(f"Fel vid sparande av preferens: {e}")
            return False

    def get_preferences(self, user_name: str) -> Dict[str, str]:
        """
        Hämta alla preferenser för en användare

        Args:
            user_name: Användarnamn

        Returns:
            Dict med preferenser
        """
        try:
            url = f"{self.supabase_url}/rest/v1/user_preferences"
            params = {
                "select": "preference_key,preference_value,confidence",
                "user_name": f"eq.{user_name}",
                "confidence": "gte.0.5",  # Endast säkra preferenser
                "order": "confidence.desc"
            }

            response = requests.get(url, headers=self.headers, params=params)

            if response.status_code == 200:
                prefs = response.json()
                return {p["preference_key"]: p["preference_value"] for p in prefs}
            else:
                return {}

        except Exception as e:
            print(f"Fel vid hämtning av preferenser: {e}")
            return {}

    def build_memory_context(self, current_query: str, user_name: Optional[str] = None) -> str:
        """
        Bygg en kontext-sträng med relevanta minnen för AI-prompten

        Args:
            current_query: Användarens nuvarande fråga
            user_name: Vem som frågar

        Returns:
            Formaterad kontext-sträng
        """
        try:
            # Sök efter relevanta minnen
            similar_memories = self.search_similar_memories(
                query=current_query,
                user_name=user_name,
                limit=3,
                threshold=0.75
            )

            # Hämta preferenser
            preferences = {}
            if user_name:
                preferences = self.get_preferences(user_name)

            # Bygg kontext
            context_parts = []

            if preferences:
                context_parts.append("ANVÄNDARPREFERENSER:")
                for key, value in preferences.items():
                    context_parts.append(f"  - {key}: {value}")

            if similar_memories:
                context_parts.append("\nRELEVANTA TIDIGARE KONVERSATIONER:")
                for i, mem in enumerate(similar_memories, 1):
                    similarity = mem.get('similarity', 0) * 100
                    context_parts.append(
                        f"  {i}. [{similarity:.0f}% likhet] "
                        f"Användare frågade: \"{mem['user_message'][:80]}...\""
                    )

            return "\n".join(context_parts) if context_parts else ""

        except Exception as e:
            print(f"Fel vid byggande av kontext: {e}")
            return ""
