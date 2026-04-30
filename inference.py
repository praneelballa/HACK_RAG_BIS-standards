import json
import time
import re
import argparse
import os
from groq import Groq
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
COLLECTION_NAME = "bis_standards"

# Initialize Engines
if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY. Set it in your environment (or in a .env file).")
groq_client = Groq(api_key=GROQ_API_KEY)
qdrant = QdrantClient(path="qdrant_db")
embed_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def extract_is_with_year(text, fallback_number):
    """Extract and normalize IS number with year from text field."""
    match = re.search(r'IS\s+(\d+[\w\s\(\)]*):(\s*\d{4})', text)
    if match:
        return f"IS {match.group(1).strip()}: {match.group(2).strip()}"
    return f"IS {fallback_number}"

def get_rag_answer(query):
    """Core RAG logic: Retrieve from Qdrant, Reason with Groq."""
    try:
        # 1. RETRIEVAL
        vector = embed_model.encode(query).tolist()
        search_results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=15
        ).points

        # 2. CONTEXT BUILDING
        context = ""
        retrieved_ids = []
        for hit in search_results:
            p = hit.payload
            is_num = p.get('is_number', 'N/A')
            title = p.get('title', p.get('Standard Title', 'N/A'))
            text = p.get('text', 'N/A')

            # ✅ Properly formatted IS number with year
            formatted_id = extract_is_with_year(text, is_num)
            retrieved_ids.append(formatted_id)
            context += f"{formatted_id}: {title}. {text}\n\n"

        # 3. REASONING
        prompt = f"""
You are an expert on Bureau of Indian Standards (BIS).

CONTEXT:
{context}

USER QUERY: {query}

TASK:
From the context above, identify the top 5 most relevant IS Standards.

STRICT RULES:
- Only use IS numbers that appear in the context above.
- Do NOT invent or hallucinate IS numbers.
- Return ONLY a valid JSON array, no extra text or markdown.
- Format:
[
  {{"is_number": "IS XXXX: YYYY", "reasoning": "..."}},
  {{"is_number": "IS YYYY: YYYY", "reasoning": "..."}},
  {{"is_number": "IS ZZZZ: YYYY", "reasoning": "..."}},
  {{"is_number": "IS AAAA: YYYY", "reasoning": "..."}},
  {{"is_number": "IS BBBB: YYYY", "reasoning": "..."}}
]
- Rank by relevance, most relevant first.
- If nothing is relevant, return [].
"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        # 4. PARSING
        raw_content = response.choices[0].message.content
        clean_json = raw_content.replace('```json', '').replace('```', '').strip()
        parsed = json.loads(clean_json)

        # ✅ Match LLM output back to properly formatted retrieved IDs
        standards_list = []
        for item in parsed:
            raw = item.get("is_number", "").replace("IS ", "").strip()
            # Find the matching formatted ID from what we retrieved
            match = next(
                (rid for rid in retrieved_ids if raw.split(":")[0].strip() in rid),
                item.get("is_number")
            )
            standards_list.append(match)

        return standards_list

    except Exception as e:
        print(f"[WARNING] Query failed: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Run inference for BIS RAG")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    with open(args.input, 'r') as f:
        test_data = json.load(f)

    results = []
    print(f"🚀 Running inference on {len(test_data)} queries...")

    for item in tqdm(test_data):
        query_id = item.get("id")
        query = item.get("query")
        expected = item.get("expected_standards", [])  # ✅ Grab from input

        start_time = time.time()
        standards = get_rag_answer(query)
        latency = round(time.time() - start_time, 4)

        results.append({
            "id": query_id,
            "retrieved_standards": standards,
            "expected_standards": expected,   # ✅ Include in output
            "latency_seconds": latency
        })

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"\n✅ Done! Results saved to {args.output}")


if __name__ == "__main__":
    main()
