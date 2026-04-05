# Backend Analysis: Context Engineering Gaps

> Date: 2026-04-05
> Scope: RAG pipeline, LangGraph agents, embedding, storage, scraping, API

---

## 1. Embedder — Wrong Library

**File:** `backend/src/pixelpersona/processing/embedder.py`

**Issue:** The `LocalEmbedder` is implemented using `langchain_huggingface.HuggingFaceEmbeddings`, but the plan (`2026-03-26-backend-implementation.md`) explicitly calls for `sentence_transformers.SentenceTransformer` with a custom class implementing the LangChain `Embeddings` interface.

```python
# Current (uses LangChain wrapper, loses direct control):
from langchain_huggingface import HuggingFaceEmbeddings
return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, ...)

# Planned (direct sentence-transformers with LangChain interface):
from sentence_transformers import SentenceTransformer
class LocalEmbedder(Embeddings):
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        ...
```

**Impact:** The LangChain wrapper adds an extra abstraction layer. More critically, the plan-defined `embed_documents` (plural) method that handles batch embedding with `batch_size` and `show_progress_bar` cannot be controlled when delegating to LangChain's wrapper. The current implementation is a thin proxy that doesn't expose the full sentence-transformers batch API.

---

## 2. Missing Gutenberg Scraper

**File:** `backend/src/pixelpersona/scraping/__init__.py`

**Issue:** The plan includes a `GutenbergScraper` in `scraping/gutenberg.py` that searches Gutendex.com and Archive.org for primary source documents. This was in the project spec (`CLAUDE.md`) and the implementation plan but was never created.

The `__init__.py` only exports:
```python
from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
__all__ = ["WikipediaScraper", "WikiquoteScraper"]
```

**Impact:** Each persona is only ingesting from 2 sources (Wikipedia + Wikiquote) instead of the planned 3. Autobiographies, letters, and primary documents from Gutenberg/Archive.org are missing, which means the RAG context for each persona is less comprehensive than designed.

---

## 3. PersonaRetriever — Rephraser Disabled

**File:** `backend/src/pixelpersona/retrieval/retriever.py` (lines 40–43)

**Status: FIXED**

The rephraser was intentionally bypassed. The fix re-enables `await self.rephraser.rephrase(query)` in the `retrieve()` method so user queries are transformed before embedding.

```python
# Before (disabled):
rephrased_query = query

# After (enabled):
rephrased_query = await self.rephraser.rephrase(query)
```

---

## 4. PersonaRetriever — Sync-over-Async in Tool

**File:** `backend/src/pixelpersona/agents/persona_agent.py` (lines 66–73)

**Status: FIXED**

The `retrieve_context` tool was a synchronous function calling `asyncio.run()` on every invocation. The tool is now `async def` so `await self.retriever.retrieve(...)` is called directly with no event loop overhead.

```python
# Before (sync tool, asyncio.run per call):
def retrieve_context(query: str) -> str:
    results = asyncio.run(self.retriever.retrieve(...))

# After (async tool, direct await):
async def retrieve_context(query: str) -> str:
    results = await self.retriever.retrieve(...)
```

---

## 5. LangChain `create_agent` — API Compatibility

**File:** `backend/src/pixelpersona/agents/persona_agent.py` (line 4, 144)

**Status: NOT AN ISSUE**

Context7 verification confirms:
- `langchain.agents.create_agent` is the **current canonical API** for LangChain v1 — the migration guide explicitly shows moving *from* `langgraph.prebuilt.create_react_agent` *to* `langchain.agents.create_agent`
- `SummarizationMiddleware` from `langchain.agents.middleware` is a documented, built-in middleware alongside `PIIMiddleware` and `HumanInTheLoopMiddleware`

The original analysis was incorrect. This is the correct modern LangChain v1 pattern.

---

## 6. Streaming is Non-Streaming

**File:** `backend/src/pixelpersona/api/routes.py`, `frontend/js/chat/ChatManager.js`, `frontend/api/client.js`

**Status: FIXED (streaming removed)**

Removed SSE streaming entirely. The `/chat/stream` endpoint was removed from the backend. The frontend now uses a new `chatRequest()` function that calls the non-streaming `/chat` endpoint and awaits the full response. The typewriter effect still runs character-by-character on the complete response, preserving the animated "chatty" feel without SSE complexity.

**Changes:**
- Backend: removed `/chat/stream` endpoint
- Frontend `client.js`: added `chatRequest()` for non-streaming POST
- Frontend `ChatManager.js`: replaced `_streamPersonaResponse` with `_requestPersonaResponse` using `chatRequest`

---

## 7. Missing Ingestion Script

**File:** `backend/scripts/ingest_persona.py`

**Issue:** Referenced in the plan but **never created**. There is no CLI script to run the full ingestion pipeline (scrape → validate → chunk → embed → store in Chroma).

**Impact:** Data ingestion must be done manually or via ad-hoc scripts. This means:
- No standardized way to populate Chroma for each persona
- No documented workflow for adding new personas
- Chroma collections may be empty or inconsistently populated

The frontend's `initNPCs()` fetches from `/personas` which returns hardcoded persona data — it does NOT verify that Chroma contains actual ingested content for those personas.

---

## 8. ChromaCollectionManager — Per-Collection Persistence Path

**File:** `backend/src/pixelpersona/storage/chroma_client.py` (lines 28–32)

**Status: INTENTIONAL**

Each persona uses a separate Chroma persist subdirectory (`chroma_data/Albert_Einstein/`, etc.). This is by design for persona data isolation. Not an issue.

---

## 9. ChromaCollectionManager — No Metadata Filtering

**File:** `backend/src/pixelpersona/storage/chroma_client.py` (lines 48–61)

```python
def similarity_search(
    self,
    query: str,
    k: int = 5,
    filter: Optional[dict] = None,
    **kwargs
) -> List[Document]:
    return self._vector_store.similarity_search(
        query=query, k=k, filter=filter, **kwargs
    )
```

**Issue:** Each persona already has their own Chroma collection (via separate persist directories). However, the metadata `filter` parameter is passed through but the documents inserted into Chroma **don't include the persona name as a metadata field on each chunk**.

When chunks are added in `PersonaVectorStore.add_documents()`, the metadata comes from the ingestion pipeline. If `source_type` is set but `persona` metadata is not consistently set on every chunk, persona-level filtering relies entirely on the collection separation — which is fragile if collections are ever merged.

---

## 10. ValidationError — Defined but Never Raised

**File:** `backend/src/pixelpersona/processing/validator.py` (line 5)

**Status: FIXED**

`DataValidator.validate()` and `validate_content()` now raise `ValidationError` on failure instead of returning `bool`. The exception class was already defined but unused — it now does its job.

```python
# Before (silent bool):
if word_count < 10:
    return False

# After (explicit exception):
if word_count < 10:
    raise ValidationError(f"Content has fewer than 10 words ({word_count} found)")
```

---

## 11. config.py — No Validation

**File:** `backend/src/pixelpersona/config.py`

```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # could be None
```

**Issue:** If `GROQ_API_KEY` is not set, the application will fail at runtime only when an LLM call is made — not at startup. There is no startup validation to catch missing environment variables early.

**Impact:** A missing API key surfaces as a cryptic LangChain/Groq error at request time, not during application startup. This delays diagnosis.

---

## 12. CORS — Double Middleware

**File:** `backend/src/pixelpersona/api/routes.py` (lines 17–33)

**Status: FIXED**

Removed the custom `@app.middleware("http")` that was duplicating CORS headers. The `CORSMiddleware` alone handles everything correctly — preflight `OPTIONS` requests, credential headers, and proper header layering.

```python
# Removed:
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    ...

# Kept (sufficient):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Summary Table

| # | Severity | Component | Issue | Status |
|---|----------|-----------|-------|--------|
| 1 | Medium | Embedder | Wrong library — LangChain wrapper instead of direct sentence-transformers | Intentional hold |
| 2 | High | Scraping | Gutenberg scraper missing — only 2/3 sources implemented | Intentional hold |
| 3 | Medium | Retrieval | Rephraser disabled — poor query terms go directly to vector search | **FIXED** |
| 4 | Medium | Agent | `asyncio.run()` in sync tool — event loop overhead per tool call | **FIXED** |
| 5 | Medium | Agent | `create_agent` + `SummarizationMiddleware` — potentially deprecated API | **NOT AN ISSUE** (verified via Context7) |
| 6 | Medium | API | SSE endpoint is buffered, not truly streaming | **FIXED** (streaming removed) |
| 7 | High | Ingestion | No ingestion script — no way to populate Chroma | On hold |
| 8 | Low | Storage | Per-collection subdirectories — intentional for persona isolation | Intentional |
| 9 | Low | Storage | Metadata filtering underutilized given collection separation | On hold |
| 10 | Low | Validation | `ValidationError` defined but never raised | **FIXED** |
| 11 | Low | Config | No startup validation for required env vars | On hold |
| 12 | Low | API | Duplicate CORS middleware | **FIXED** |

---

## Critical Path (Issues blocking functional RAG pipeline)

1. **#2 Missing Gutenberg Scraper** — Persona data is 33% less rich than designed
2. **#7 Missing Ingestion Script** — No standardized way to populate Chroma; Chroma may have zero documents
3. **#6 Non-Streaming SSE** — Frontend receives buffered response; no incremental tokens
4. **#3 Rephraser Disabled** — Retrieval quality degradation for natural language queries
5. **#1 Wrong Embedder** — Cannot control batching/progress; less efficient than designed
