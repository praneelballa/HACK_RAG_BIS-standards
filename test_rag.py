from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(path="qdrant_db")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')

query = "High strength cement for structural work"
query_vector = model.encode(query).tolist()

results = client.search(
    collection_name="bis_standards",
    query_vector=query_vector,
    limit=3
)

print(f"\nResults for: '{query}'")
for res in results:
    print(f"ID: {res.payload['is_number']} | Score: {res.score:.4f}")
    print(f"Text: {res.payload['text'][:100]}...\n")