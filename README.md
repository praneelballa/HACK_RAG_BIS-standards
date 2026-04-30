# BIS Standard Recommendation Engine
### BIS × Sigma Squad AI Hackathon 2026

An AI-powered RAG pipeline that recommends relevant Bureau of Indian Standards (BIS) codes from a product description — in under 5 seconds.

---

## Results
| Metric | Score | Target |
|---|---|---|
| Hit Rate @3 | 100% | >80% |
| MRR @5 | 0.90 | >0.7 |
| Avg Latency | ~3.5s | <5s |

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Groq API key
```bash
# Windows (PowerShell)
$env:GROQ_API_KEY = "your_key_here"

# Linux/Mac
export GROQ_API_KEY="your_key_here"
```

### 3. (One-time) Build the local vector DB
If `qdrant_db/` is already present and populated, you can skip this.

```bash
python parser.py          # creates raw_standards.json from dataset.pdf
python chunker.py         # creates processed_chunks.json
python vector_store.py    # creates/loads qdrant_db and uploads vectors
```

### 4. Run inference (for judges)
```bash
python inference.py --input public_test_set.json --output team_results.json
```

### 5. Evaluate results
```bash
python eval_script.py --results team_results.json
```

### 6. Run the UI
```bash
streamlit run UI.py
```

---

## Project Structure
```
/
├── inference.py           ← Judge entry point
├── eval_script.py         ← Evaluation script
├── app.py                 ← Core RAG logic
├── UI.py                  ← Streamlit dashboard
├── parser.py              ← PDF parser
├── chunker.py             ← Semantic chunker
├── vector_store.py        ← Qdrant indexer
├── qdrant_db/             ← Local vector database
├── requirements.txt
└── README.md
```

---

## Architecture
```
Product Description
        ↓
Query Expansion
        ↓
Semantic Search (Qdrant + BGE-Small-EN)
        ↓
Re-ranking (Llama 3.3 70B via Groq)
        ↓
Top 3-5 BIS Standards + Reasoning
```

---

## Tech Stack
- **LLM:** Llama 3.3 70B via Groq
- **Vector DB:** Qdrant (local)
- **Embeddings:** BAAI/bge-small-en-v1.5
- **Framework:** Python + Streamlit
- **Data:** BIS SP 21 PDF (1197 standards, 1374 chunks)

`markdown
---

## Developer Operations & Troubleshooting

### 🛑 Handling Database Lock Errors
If the system throws an `EBUSY: resource busy or locked` error, it means a background Python process or OneDrive is holding the Qdrant database.

1. **Force Close Processes**:
   ```powershell
   # Wipe all background Python instances
   taskkill /F /IM python.exe /T
````

2. **Clear Manual Lock**:
   Navigate to `qdrant_db/` and delete the `.lock` file manually.

3. **Storage Best Practice**:
   Ensure the project is **not** running inside a OneDrive or Dropbox synced folder to avoid real-time file conflicts during indexing.

---

### ⚙️ Performance Tuning

* **Latency Control**: To maintain the **~3.5s latency**, the system uses `Llama-3.3-70B-Specdec`. If latency spikes, verify your Groq rate limits.
* **In-Memory Fallback**: For environments where disk I/O is restricted, the `QdrantClient` can be switched to `:memory:` in `app.py`, though this requires re-indexing on every launch.

---

## Model Configuration & Tuning

| Component         | Choice                   | Rationale                                                                 |
| ----------------- | ------------------------ | ------------------------------------------------------------------------- |
| **Embeddings**    | BGE-Small-EN-v1.5        | Optimized for technical documentation & low CPU overhead.                 |
| **Reasoning**     | Llama 3.3 70B            | High-parameter reasoning to eliminate hallucinated IS numbers.            |
| **Chunking**      | Semantic                 | Prevents splitting standard descriptions across multiple vectors.         |
| **Hybrid Weight** | 0.7 Vector / 0.3 Keyword | Prioritizes semantic meaning while retaining keyword accuracy for IS IDs. |

---

## Future Roadmap

* [ ] **Multi-modal Support**: Direct image-to-standard mapping for construction site safety checks.
* [ ] **Offline LLM**: Quantized Llama-3 (8B) integration for 100% air-gapped environments.
* [ ] **Automated PDF Sync**: Direct integration with the BIS website for real-time standard updates.

---

### Sigma Squad AI

**Authors:** [Your Name/Team Members]
**Last Updated:** April 2026
**Status:** Hackathon Submission Ready

```
