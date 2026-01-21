# Development Guide

## Prerequisites

- Python 3.10+
- pip or conda
- HuggingFace API token

## Setup

```bash
# Clone and setup
git clone <repo>
cd rag-quiz

# Virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Dependencies
pip install -r requirements.txt

# Configuration
copy .env.example .env
# Add HUGGINGFACEHUB_API_TOKEN to .env
```

## Project Structure

```
rag-quiz/
├── app_c.py              # Main application
├── setup_core.py         # LLM & embeddings initialization
├── requirements.txt      # Python dependencies
├── .env.example         # Configuration template
├── Dockerfile           # Production container
├── README.md            # Project overview
├── ARCHITECTURE.md      # System design
├── CONFIGURATION.md     # Configuration reference
├── DEVELOPMENT.md       # This file
├── TECH_SUMMARY.md      # Technical summary
├── PRODUCTION_CHECKLIST.md # Deployment guide
├── modules/
│   ├── file_handler.py  # PDF loading
│   ├── rag_engine.py    # RAG pipeline
│   ├── prompts.py       # LLM prompts
│   └── __init__.py
└── temp_sessions/       # Runtime session storage
```

## Running Locally

```bash
chainlit run app_c.py -w
```

Open `http://localhost:8000` in your browser.

## Before Production Deployment

**Pre-deployment checklist:**

1. ✅ **Code Quality** - Type hints (100%), error handling, logging (65+ points)
2. ✅ **Configuration** - Set environment variables for production
3. ✅ **Security** - API tokens in secure credential manager
4. ✅ **Monitoring** - Configure log aggregation (ELK, CloudWatch, etc.)
5. ✅ **Testing** - Load test with production-scale documents
6. ✅ **Deployment** - Use Docker or configure web server (nginx, gunicorn)
7. ✅ **SSL/TLS** - Configure reverse proxy with SSL certificates
8. ✅ **Rate Limiting** - Set up if needed for public access

For complete pre-deployment checklist, see PRODUCTION_CHECKLIST.md.

## Running Locally

```bash
# Development mode with auto-reload
python -m chainlit run app_c.py -w

# Production mode
python -m chainlit run app_c.py

# Custom port
python -m chainlit run app_c.py --port 8001
```

Browse to `http://localhost:8000`

## Key Modules

### `app_c.py` - Main Application

**Config Class**
- Environment-based configuration
- Validation on startup
- Type hints for all settings

**Core Functions**
- `load_pdf_files()` - Load PDFs into documents
- `perform_semantic_analysis()` - Chunk documents semantically
- `create_and_store_vectorstore()` - Create indices
- `index_files_workflow()` - Orchestrate PDF indexing
- `refine_question()` - Improve user queries with context
- `handle_error()` - Centralized error handling
- `main()` - Message processing pipeline

**Event Handlers**
- `start()` - Session initialization
- `end()` - Session cleanup
- `main()` - Message handling

### `setup_core.py` - LLM Setup

```python
init_llm()         # Returns ChatHuggingFace instance
init_embeddings()  # Returns embeddings model
```

### `modules/file_handler.py`

```python
save_and_load_pdf(file, path)  # Upload and load PDF
cleanup_folder(path)            # Clean session directory
```

### `modules/rag_engine.py`

```python
split_documents(docs)                    # Semantic chunking
create_vectorstore(chunks, existing)     # Index chunks
get_hybrid_retriever(vectorstore, docs)  # Create retriever
```

## Coding Standards

### Type Hints
```python
async def load_pdf_files(
    files: List[cl.File],
    session_path: str,
    step: cl.Step
) -> List[Document]:
    """Load and process PDF files into documents."""
```

### Logging
```python
logger.debug(f"Function called with {len(files)} files")    # Details
logger.info(f"Processing started for {name}")                # Milestones
logger.warning("Non-critical issue detected")                # Cautions
logger.error("Operation failed", exc_info=e)                 # Errors
```

### Error Handling
```python
try:
    result = await some_operation()
except SomeError as e:
    await handle_error(e, "User-friendly message", step)
    raise
```

### Docstrings
```python
async def my_function(param: str) -> List[str]:
    """
    Brief description.
    
    Args:
        param: Description
        
    Returns:
        Description of return value
    """
```

## Common Tasks

### Add New Configuration Option

1. Add to `Config` class in `app_c.py`:
```python
MY_SETTING: str = os.getenv("MY_SETTING", "default_value")
```

2. Add to `.env.example`:
```
MY_SETTING=value
```

3. Update `CONFIGURATION.md`

### Add New Log Point

```python
logger.debug(f"Processing item {i}: {data}")
logger.info(f"Step completed in {elapsed:.2f}s")
```

### Add New Error Scenario

```python
if condition:
    error_msg = "What went wrong"
    await handle_error(CustomError(msg), error_msg, step)
    return None
```

### Improve Type Safety

```python
# Before
async def process(data):
    return result

# After  
async def process(data: Dict[str, Any]) -> List[Document]:
    return result
```

## Debugging

### Enable Debug Logging
```bash
# In .env
LOG_LEVEL=DEBUG
```

### Inspect Session Data
```python
# Add to handler
print(cl.user_session.get("vectorstore"))
print(cl.user_session.get("all_splits"))
```

### Test Specific Function
```python
# In main or separate script
async def test_function():
    result = await load_pdf_files(files, path, step)
    print(result)

asyncio.run(test_function())
```

## Performance Optimization

### Profiling
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... code to profile ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

### Caching
Consider caching for:
- Embeddings model (expensive to load)
- Chunked documents (if same PDFs uploaded multiple times)
- Vector indices (if documents don't change)

### Async Optimization
All I/O operations use `cl.make_async()` for non-blocking execution

## Testing Approach

Current tests cover:
- Configuration loading and validation
- Import verification
- Basic type checking

Recommended additions:
- Unit tests for RAG pipeline
- Integration tests for full workflow
- Load testing for concurrent users
- Semantic quality evaluation

## Deployment

### Docker
```bash
docker build -t rag-quiz .
docker run -p 8000:8000 -e HUGGINGFACEHUB_API_TOKEN=$TOKEN rag-quiz
```

### Environment Variables (Production)
```
LOG_LEVEL=WARNING
CONVERSATION_HISTORY_MESSAGES=5
HUGGINGFACEHUB_API_TOKEN=<secure>
TEMP_SESSIONS_FOLDER=/var/sessions
```

### Monitoring
- Monitor logs for errors
- Track API rate limits (HuggingFace)
- Monitor memory usage (embeddings model)
- Track response times

## Common Issues

### "No HuggingFace token"
- Set `HUGGINGFACEHUB_API_TOKEN` in `.env`
- Or set `HF_TOKEN` environment variable

### "FAISS not found"
- `pip install faiss-cpu` (or `faiss-gpu`)

### "Slow semantic chunking"
- Normal for first use (model download/init)
- Caching will speed up subsequent runs

### "Session cleanup fails"
- Check directory permissions
- Ensure no file locks on session files

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Follow coding standards above
3. Add tests for new functionality
4. Update documentation
5. Submit PR with clear description

## Resources

- [Chainlit Docs](https://docs.chainlit.io/)
- [LangChain Docs](https://python.langchain.com/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [HuggingFace Models](https://huggingface.co/models)
