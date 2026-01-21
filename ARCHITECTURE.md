# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Chainlit Frontend                       │
│                 (Web UI for Chat Interface)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    app_c.py (Main App)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Event Handlers (on_chat_start, on_message, etc.)     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Core Workflows                                       │   │
│  │ • index_files_workflow()  - Process PDFs            │   │
│  │ • load_pdf_files()        - Load documents          │   │
│  │ • perform_semantic_analysis() - Chunk documents     │   │
│  │ • create_and_store_vectorstore() - Index chunks     │   │
│  │ • refine_question()       - Improve queries         │   │
│  │ • handle_error()          - Centralized errors      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐    ┌──────────┐    ┌─────────────┐
   │ modules │    │setup_core│    │Config Class │
   └─────────┘    └──────────┘    └─────────────┘
        │              │
        ├──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   ┌──────────────────┐    ┌────────────────────┐
   │  RAG Pipeline    │    │  LLM & Embeddings  │
   │                  │    │                    │
   │ • file_handler   │    │ • HuggingFace LLM │
   │ • rag_engine     │    │ • Embeddings model │
   │ • prompts        │    │                    │
   └──────────────────┘    └────────────────────┘
        │
   ┌────┴─────────────────────────────────────┐
   ▼                                           ▼
┌─────────────────┐                   ┌──────────────────┐
│  FAISS Vector   │                   │  BM25 Retriever  │
│    Store        │                   │                  │
│ (Semantic)      │                   │  (Keyword-based) │
└─────────────────┘                   └──────────────────┘
   │
   └───────────────────────┬──────────────────┐
                           ▼                  ▼
                    ┌──────────────┐  ┌──────────────┐
                    │ Session Data │  │ PDF Files    │
                    │ (File-based) │  │ (Temporary)  │
                    └──────────────┘  └──────────────┘
```

## Component Descriptions

### Frontend Layer
- **Chainlit**: Modern chat UI framework
- Handles user messages, file uploads, message streaming

### Application Core (`app_c.py`)
- **Configuration Management**: Environment-based settings via `Config` class
- **Error Handling**: Centralized error handler with consistent logging
- **Event Orchestration**: Manages Chainlit lifecycle events
- **Workflow Orchestration**: Coordinates RAG pipeline

### Modules

#### `modules/file_handler.py`
- PDF loading and storage
- File path management
- Metadata enrichment (source, page info)

#### `modules/rag_engine.py`
- Semantic document chunking with embeddings
- Vector store creation (FAISS)
- Hybrid retriever combining FAISS + BM25
- Document deduplication

#### `modules/prompts.py`
- System prompts for LLM
- Query refinement instructions
- Answer generation templates

### External Services

#### `setup_core.py`
- LLM initialization (Meta-Llama-3.1-8B-Instruct)
- Embeddings model initialization (multilingual)
- HuggingFace integration

### Data Flow

```
User Upload
    │
    ▼
load_pdf_files()
    │ PDFs loaded as Documents
    ▼
perform_semantic_analysis()
    │ Semantic chunks created
    ▼
create_and_store_vectorstore()
    │ Chunks indexed in FAISS
    │ BM25 index created
    ▼
Session Storage (vectorstore, retriever)

────────────────────────────────

User Query
    │
    ▼
refine_question() → consider conversation history
    │ Refined query
    ▼
Hybrid Retriever (FAISS + BM25)
    │ Retrieved documents
    ▼
LLM with context
    │ Generated answer
    ▼
get_sources_elements()
    │ Extract source PDFs
    ▼
Send to UI with citations
```

## Key Design Decisions

### 1. Hybrid Retrieval
- **FAISS**: Semantic similarity (embeddings-based)
- **BM25**: Keyword matching (sparse vector search)
- **Ensemble**: Combines both for better recall

### 2. Session Management
- File-based storage (temporary directory)
- Per-user sessions via Chainlit
- Automatic cleanup on session end

### 3. Error Handling
- Centralized `handle_error()` function
- Consistent logging with context
- User-friendly error messages
- Graceful degradation

### 4. Configuration
- Environment variables for flexibility
- Sensible defaults for development
- Validation on startup
- Support for multiple environments

### 5. Logging
- Function-level tracing with line numbers
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Performance timing information
- Full exception context

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Chainlit | Chat interface |
| LLM | Meta-Llama-3.1-8B-Instruct | Text generation |
| Embeddings | paraphrase-multilingual-mpnet | Semantic similarity |
| Vector DB | FAISS | Fast similarity search |
| BM25 | rank-bm25 | Keyword retrieval |
| Chunking | LangChain SemanticChunker | Smart document splitting |
| Runtime | Python 3.10+ | Async/await support |

## Scalability Considerations

### Current Limitations
- File-based session storage (not distributed)
- Single FAISS index per session (not persistent)
- No session persistence across restarts

### Production Recommendations
1. Use persistent vector database (Pinecone, Weaviate)
2. Implement distributed session storage (Redis, database)
3. Add caching layer for frequent queries
4. Implement request rate limiting
5. Add comprehensive monitoring and alerting

## Security Considerations

1. **HuggingFace Token**: Should be managed via secrets (not in `.env`)
2. **File Uploads**: Validate file types and sizes
3. **Session Data**: Clean up sensitive data on session end
4. **LLM Outputs**: May contain hallucinations - review before critical use
5. **Resource Limits**: Implement timeouts and memory limits

## Performance Characteristics

- **PDF Loading**: O(file_size) - scales with document
- **Semantic Chunking**: O(n*log(n)) - uses embeddings model
- **Indexing**: O(n*d) where n=chunks, d=embedding_dim
- **Retrieval**: O(log n) FAISS + O(n) BM25 (hybrid ensemble)
- **LLM Response**: O(context_length) - varies by model

## Testing Strategy

Current: Configuration and import validation
Recommended:
- Unit tests for each module
- Integration tests for RAG pipeline
- Load testing for concurrent users
- Semantic quality evaluation of retrieval
