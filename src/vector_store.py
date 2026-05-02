    from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import json

# 1. Initialize Model & Client
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
client = QdrantClient(path="qdrant_db") # This creates a local database folder

def upload_to_qdrant():
    with open("processed_chunks.json", "r") as f:
        chunks = json.load(f)

    # 2. Create Collection
    client.recreate_collection(
        collection_name="bis_standards",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 3. Batch Upload
    points = []
    for i, chunk in enumerate(chunks):
        # Generate the 384-dim vector
        vector = model.encode(chunk['content']).tolist()
        
        points.append(PointStruct(
            id=i,
            vector=vector,
            payload={
                "text": chunk['content'],
                "is_number": chunk['metadata']['is_number'],
                "category": chunk['metadata']['category']
            }
        ))
        
        # Upload in batches of 100 for speed
        if len(points) >= 100:
            client.upsert(collection_name="bis_standards", points=points)
            points = []
            print(f"Uploaded {i+1} vectors...")

    if points:
        client.upsert(collection_name="bis_standards", points=points)

    print("🚀 All vectors uploaded to Qdrant successfully!")

if __name__ == "__main__":
    upload_to_qdrant()