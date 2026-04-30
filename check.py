from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

try:
    print("🔄 Loading Embedding Model...")
    model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    print("🔄 Connecting to Local Qdrant...")
    client = QdrantClient(path="qdrant_db")
    
    query = "Drinking water storage tank design and sanitary fittings"
    print(f"🔍 Searching for: '{query}'")
    
    vector = model.encode(query).tolist()
    
    # Using the more explicit 'search' call
    search_result = client.query_points(
        collection_name="bis_standards",
        query=vector,
        limit=5
    ).points
    
    if not search_result:
        print("❌ Search returned 0 results.")
    else:
        print(f"✅ Found {len(search_result)} matches:")
        print("-" * 50)
        for hit in search_result:
            # Note: payload access might differ slightly in query_points
            p = hit.payload
            print(f"Score: {hit.score:.4f} | IS {p.get('is_number', 'N/A')}")
            print(f"Text: {p.get('text', 'No text')[:150]}...")
            print("-" * 50)

except Exception as e:
    print(f"💥 An error occurred: {e}")