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

---

## Developer Operations

- **Database Lock Handling:** Resolve `EBUSY` errors caused by active Python processes or file locks  
- **Process Cleanup:** Terminate background Python instances using system-level commands  
- **Manual Recovery:** Remove `.lock` files from `qdrant_db/` when required  
- **Storage Constraint:** Avoid running inside cloud-synced directories (OneDrive/Dropbox) to prevent conflicts  

---

## Performance & Optimization

- **Latency:** ~3.5s average response time  
- **Inference Engine:** Llama 3.3 70B with speculative decoding via Groq  
- **Rate Limiting:** Dependent on Groq API limits  
- **Fallback Mode:** Supports in-memory vector store (`QdrantClient: :memory:`) for restricted environments  

---

## Model Configuration

- **Embeddings:** BAAI/bge-small-en-v1.5 (low CPU, optimized for technical text)  
- **Reasoning Model:** Llama 3.3 70B (reduces hallucinated IS standards)  
- **Chunking Strategy:** Semantic chunking to preserve context  
- **Retrieval Strategy:** Hybrid search (0.7 vector similarity / 0.3 keyword matching)  

---

## System Design Notes

- **Vector Storage:** Local Qdrant database with optional volatile mode  
- **Indexing Strategy:** Chunk-level embedding for standard-level retrieval  
- **Failure Handling:** Graceful fallback for locked or restricted storage environments  

---

## Future Roadmap

- **Multi-modal Support:** Image-to-standard mapping for safety/compliance use cases  
- **Offline Capability:** Quantized Llama 3 (8B) for air-gapped deployments  
- **Live Data Sync:** Automated ingestion from BIS sources for real-time updates  

---

## Project Metadata

- **Team:** Sigma Squad AI  
- **Status:** Hackathon Submission Ready  
- **Last Updated:** April 2026  