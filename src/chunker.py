import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

def prepare_chunks():
    with open("raw_standards.json", "r") as f:
        standards = json.load(f)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    processed_chunks = []

    for item in standards:  # ✅ Everything below is indented inside this loop
        header = f"Standard: {item.get('full_is_id', 'IS ' + item['is_number'])}" \
                 f" Title: {item['title']} Category: {item['category']}. "
        chunks = text_splitter.split_text(item['scope'])
        for chunk in chunks:
            processed_chunks.append({
                "content": header + chunk,
                "metadata": {
                    "is_number": item['is_number'],
                    "full_is_id": item.get('full_is_id', f"IS {item['is_number']}: {item['year']}"),
                    "title": item['title'],
                    "category": item['category']
                }
            })

    with open("processed_chunks.json", "w") as f:
        json.dump(processed_chunks, f, indent=4)
    print(f"✅ Created {len(processed_chunks)} chunks from {len(standards)} standards.")

if __name__ == "__main__":
    prepare_chunks()