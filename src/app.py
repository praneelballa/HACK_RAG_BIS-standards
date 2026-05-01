import json
from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
from pathlib import Path
import tomllib

# --- CONFIG ---
load_dotenv()
COLLECTION_NAME = "bis_standards"

_groq_client = None
_groq_client_key = None
_qdrant = None
_embed_model = None


def _get_groq_api_key() -> str | None:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key

    # When running under Streamlit, allow `.streamlit/secrets.toml` as source of truth.
    try:
        import streamlit as st  # type: ignore

        try:
            secret_val = st.secrets["GROQ_API_KEY"]
        except Exception:
            secret_val = None

        if secret_val:
            return str(secret_val)
    except Exception:
        pass

    # Fallback: parse `.streamlit/secrets.toml` directly (works even if Streamlit secrets
    # integration isn't available for some reason).
    try:
        secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            data = tomllib.loads(secrets_path.read_text(encoding="utf-8"))
            val = data.get("GROQ_API_KEY")
            if val:
                return str(val)
    except Exception:
        pass

    return None


def _get_groq_client() -> Groq:
    global _groq_client, _groq_client_key

    api_key = _get_groq_api_key()
    if not api_key:
        raise RuntimeError(
            "Missing GROQ_API_KEY. Set it as an environment variable, in a .env file, "
            "or in .streamlit/secrets.toml."
        )

    if _groq_client is None or _groq_client_key != api_key:
        _groq_client = Groq(api_key=api_key)
        _groq_client_key = api_key

    return _groq_client


def _get_qdrant() -> QdrantClient:
    global _qdrant
    if _qdrant is None:
        # Adding a timeout or preferred connection method can help
        _qdrant = QdrantClient(path="qdrant_db", prefer_grpc=False)
    return _qdrant


def _get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    return _embed_model


def ask_bis(query):
    groq_client = _get_groq_client()
    qdrant = _get_qdrant()
    embed_model = _get_embed_model()
    # 1. RETRIEVAL
    vector = embed_model.encode(query).tolist()
    search_results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=10  # ✅ Fetch more, LLM picks best 3
    ).points

    # 2. CONTEXT BUILDING
    context = ""
    for hit in search_results:
        p = hit.payload
        is_num = p.get('is_number', 'N/A')
        title = p.get('title', 'N/A')
        text = p.get('text', 'N/A')
        context += f"IS {is_num}: {title}. {text}\n\n"

    # 3. REASONING (Groq + Llama 3.3 70B)
    prompt = f"""
You are a BIS (Bureau of Indian Standards) expert.

CONTEXT:
{context}

USER QUERY: {query}

TASK:
From the context above, identify the top 3 most relevant IS Standards.

STRICT RULES:
- Only use IS numbers that appear in the context above.
- Do NOT invent or hallucinate IS numbers.
- Return ONLY a valid JSON array, no extra text or markdown.
- Format:
[
  {{"is_number": "XXXX", "reasoning": "..."}},
  {{"is_number": "YYYY", "reasoning": "..."}},
  {{"is_number": "ZZZZ", "reasoning": "..."}}
]
- Rank by relevance, most relevant first.
- If nothing is relevant, return [].
"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        content = response.choices[0].message.content
        clean = content.replace('```json', '').replace('```', '').strip()
        return json.loads(clean)  # ✅ Returns actual list, not raw string

    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parse failed: {e}")
        print(f"[RAW]: {content}")
        return []
    except Exception as e:
        print(f"[ERROR] {e}")
        return []

if __name__ == "__main__":
    # Test a real query to see Groq in action
    try:
        print("🚀 Sending request to Groq...")
        result = ask_bis("I need standards for drinking water storage tanks")
        print("\n--- FINAL JSON OUTPUT ---")
        print(result)
    except Exception as e:
        print(f"❌ Run failed: {e}")    