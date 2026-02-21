# PDF Crawler + PDF Chatbot (RAG) 

This project contains **two runnable entrypoints**:

➡️ **(1) Crawler CLI**: crawls a seed URL, finds PDF links, downloads PDFs, and writes `manifest.json`  
➡️ **(2) Chatbot**: a **FastAPI** HTTP API (plus optional CLI) that answers questions using downloaded PDFs **with citations**

---

## Folder Structure (What to Look At)

```
technology1_pdf_rag/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ src/
│  └─ pdf_rag/
│     ├─ config.py
│     ├─ utils.py
│     ├─ crawler/
│     │  ├─ crawler.py          -> HTML crawler (BFS, scope + depth control)
│     │  ├─ download.py         -> PDF downloader + PDF validation + manifest writer
│     │  └─ cli.py              -> runnable crawler CLI
│     └─ rag/
│        ├─ ingest.py           -> PDF text extraction (page-level) + chunking + index persistence
│        ├─ bm25.py             -> BM25 retrieval
│        ├─ answer.py           -> deterministic answer builder + citations
│        ├─ api.py              -> FastAPI server (chat + ingest)
│        └─ cli.py              -> optional chatbot CLI
├─ data/
│  ├─ pdfs/                     -> downloaded PDFs (crawler output)
│  ├─ index/                    -> persisted index (chunks + tokenized corpus)
│  └─ manifest.json             -> crawler manifest (written at runtime)
└─ notebooks/
   └─ Untitled119.ipynb         -> original notebook you provided (reference)
```

---

## Setup

### 1) Create venv + install dependencies

```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
# (optional) install as a package for cleaner imports
pip install -e .
```

---

## Task 1 — Run the Crawler (CLI)

**Seed URL (given in exam):**  
`https://www.technology1.com/company/investors`

Run crawler with depth 2 and up to 50 PDFs:

```bash
python -m pdf_rag.crawler.cli   --start-url "https://www.technology1.com/company/investors"   --max-depth 2   --max-pdfs 50
```

**Outputs**
- PDFs saved to ➡️ `data/pdfs/`
- Manifest saved to ➡️ `data/manifest.json`

`manifest.json` items include at minimum:
- `source_url`
- `local_path`
- `downloaded_at`
- `http_status`
- plus recommended: `sha256`, `content_length`, `final_url`, `reason`

---

## Task 2 — Run the PDF Chatbot (RAG)

### Option A (Recommended): HTTP API (FastAPI)

Start the server:

```bash
uvicorn pdf_rag.rag.api:app --host 0.0.0.0 --port 8000
```

#### 1) Ingest PDFs (build index)

```bash
curl -X POST "http://localhost:8000/ingest"   -H "Content-Type: application/json"   -d '{"chunk_size": 800, "overlap": 200}'
```

#### 2) Ask a question (returns answer + citations)

```bash
curl -X POST "http://localhost:8000/chat"   -H "Content-Type: application/json"   -d '{"question": "What year is the latest annual report covering?", "top_k": 6}'
```

Response format:
```json
{
  "answer": "...",
  "sources": [
    { "pdf": "somefile.pdf", "page": 12, "snippet": "..." },
    { "pdf": "another.pdf",  "page": 3,  "snippet": "..." }
  ]
}
```

### Option B: Chatbot CLI (Optional)

If you prefer a CLI interaction:

```bash
python -m pdf_rag.rag.cli --question "What guidance or outlook is provided?" --top-k 6
```

---

## Quick Acceptance Checklist

✅ **Crawler**
1. Run crawler with `--max-depth 2` and `--max-pdfs 50`  
2. Confirm PDFs exist under `data/pdfs/`  
3. Confirm `data/manifest.json` exists and contains required fields

✅ **Chatbot**
1. Run API and call `/ingest`  
2. Call `/chat` with a sample question  
3. Confirm response contains:
   - an `answer`
   - at least **2 citations** (filename + page; snippets included)

---

## Notes on Engineering Choices

➡️ **Retrieval**: BM25 (fast, no external embeddings required)  
➡️ **Answer generation**: deterministic extractive approach using top retrieved passages  
➡️ **Citations**: returned as `{pdf, page, snippet}` for traceability  
➡️ **Robustness**: URL normalization, deduplication, scoped crawl, retries + backoff, PDF validation via content-type and `%PDF` magic bytes
