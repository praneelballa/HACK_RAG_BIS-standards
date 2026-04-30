import json
from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# --- CONFIG ---
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
COLLECTION_NAME = "bis_standards"

# Initialize Clients
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
qdrant = QdrantClient(path="qdrant_db")
embed_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def ask_bis(query):
    if not groq_client:
        raise RuntimeError("Missing GROQ_API_KEY. Set it in your environment (or in a .env file).")
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