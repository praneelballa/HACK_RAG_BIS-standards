import os
import json
from google import genai

client = genai.Client(api_key="AIzaSyB7fvQ3Unxzu4EOk_PbzJE8Zu73SCLuex0")

def get_reasoning(query, retrieved_standards):
    context_text = ""
    for idx, std in enumerate(retrieved_standards):
        context_text += f"\n--- Source {idx+1} ---\n"
        context_text += f"IS Code: {std.get('is_number', 'N/A')}\n"
        context_text += f"Title: {std.get('title', 'N/A')}\n"
        context_text += f"Details: {std.get('text', 'N/A')}\n"

    prompt = f"""
You are an expert BIS (Bureau of Indian Standards) Assistant.

USER QUERY: {query}

CONTEXT FROM STANDARDS:
{context_text}

TASK:
Based ONLY on the context provided, identify the top 3 most relevant IS Standards.
Explain why each is relevant to the user's query in 2-3 technical sentences.

STRICT RULES:
- You may ONLY reference IS numbers that appear in the CONTEXT above.
- Do NOT invent or hallucinate any IS standard numbers.
- Return ONLY a valid JSON array, no extra text or markdown.
- Format:
[
  {{"is_number": "XXXX", "reasoning": "..."}},
  {{"is_number": "YYYY", "reasoning": "..."}},
  {{"is_number": "ZZZZ", "reasoning": "..."}}
]
- Rank by relevance, most relevant first.
- If no standards are relevant, return an empty array [].
"""

    # ✅ Fixed: properly indented inside the function
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    try:
        content = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(content)
    except Exception as e:
        print(f"[WARNING] JSON parse failed: {e}")
        print(f"[RAW RESPONSE]: {response.text}")
        return []


if __name__ == "__main__":
    test_retrieval = [
        {"is_number": "12701", "title": "Polyethylene Tanks", "text": "Requirements for water storage."},
        {"is_number": "1239", "title": "Steel Tubes", "text": "Specs for mild steel tubes."},
        {"is_number": "269", "title": "Ordinary Portland Cement", "text": "Covers OPC for construction."}
    ]
    result = get_reasoning("I need a water storage tank", test_retrieval)
    print(json.dumps(result, indent=2))