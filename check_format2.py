from qdrant_client import QdrantClient
import re

qdrant = QdrantClient(path="qdrant_db")
results = qdrant.scroll("bis_standards", limit=50)

for r in results[0]:
    text = r.payload.get('text', '')
    if '2185' in text or '1489' in text:
        print("RAW TEXT:", text[:120])