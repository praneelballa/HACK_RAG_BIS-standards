from qdrant_client import QdrantClient
import re

qdrant = QdrantClient(path="qdrant_db")
results = qdrant.scroll("bis_standards", limit=10)

for r in results[0]:
    text = r.payload.get('text', '')
    match = re.search(r'IS\s+(\d+[\w\s\(\)]*:\s*\d{4})', text)
    if match:
        print("Found:", match.group(0))
    else:
        print("No year found in:", text[:80])