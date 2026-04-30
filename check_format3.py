from qdrant_client import QdrantClient

qdrant = QdrantClient(path="qdrant_db")
results = qdrant.scroll("bis_standards", limit=200)

for r in results[0]:
    text = r.payload.get('text', '')
    is_num = r.payload.get('is_number', '')
    if '2185' in text or '1489' in is_num or '2185' in is_num:
        print("IS NUMBER:", is_num)
        print("FULL TEXT:", text)
        print("---")