# RAG Quiz 📚💬

Interactive application for analyzing PDF documents using **Retrieval-Augmented Generation (RAG)** technology. Upload documents, ask questions, and get precise answers with source citations.

## ✨ Features

- 📄 **PDF Document Processing** - Upload and analyze multiple PDF files
- 🔍 **Hybrid Search** - Combines BM25 (keyword-based) and FAISS (semantic) retrieval
- 🧠 **Smart Text Chunking** - Semantic-aware document splitting for better context
- 💬 **Interactive Chat** - Conversational interface powered by Chainlit
- 🌐 **Multilingual Support** - Works with Ukrainian and English languages
- 📚 **Source Citations** - Every answer includes references to source pages
- 🧵 **Context-Aware** - Maintains conversation history for follow-up questions

## 🛠️ Technology Stack

- **Framework**: [Chainlit](https://chainlit.io/) - Modern chat UI
- **LLM**: [Hugging Face](https://huggingface.co/) - Meta-Llama-3.1-8B-Instruct
- **Embeddings**: Sentence Transformers (paraphrase-multilingual-mpnet-base-v2)
- **Vector Store**: FAISS - Fast similarity search
- **Retrieval**: LangChain with hybrid BM25 + semantic search
- **Language**: Python 3.10+

## 🚀 Quick Start

### 🌐 Live Demo

**Hugging Face Space**: [rag-quiz-demo](https://huggingface.co/spaces/ituvtu/rag-quiz-demo)  
⚠️ *Note: Space preview is not available due to platform limitations. Full preview functionality works on local deployment.*

### Local Installation

#### Prerequisites

### Prerequisites

- Python 3.10 or higher
- Hugging Face API token ([Get one here](https://huggingface.co/settings/tokens))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ituvtu/rag-quiz.git
cd rag-quiz
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your HUGGINGFACEHUB_API_TOKEN
```

### Run the Application

```bash
chainlit run app_c.py -w
```

The app will open at `http://localhost:8000`

## 📖 Usage

1. **Upload PDFs** - Drag and drop or click to upload PDF documents
2. **Wait for Processing** - The system will analyze and index your documents
3. **Ask Questions** - Type your questions in the chat interface
4. **Get Answers** - Receive accurate answers with source citations
5. **Continue Conversation** - Ask follow-up questions with context awareness

## 📁 Project Structure

```
rag-quiz/
├── app_c.py                 # Main Chainlit application
├── setup_core.py            # LLM and embeddings initialization
├── modules/
│   ├── file_handler.py      # PDF upload and processing
│   ├── rag_engine.py        # RAG pipeline (chunking, indexing, retrieval)
│   └── prompts.py           # System prompts and instructions
├── temp_sessions/           # Temporary session storage
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables (create manually)
```

## 🔧 Configuration

All configuration via environment variables (see `.env.example`):

```bash
# Required
HUGGINGFACEHUB_API_TOKEN=your_token_here

# Optional (defaults provided)
CONVERSATION_HISTORY_MESSAGES=3      # Context window for question refinement
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR
MAX_FILE_SIZE_MB=50                   # Maximum upload size
TEMP_SESSIONS_FOLDER=temp_sessions    # Session storage
```

## 👨‍💻 Development & Contributing

### Local Setup

```bash
# Clone repository
git clone https://github.com/ituvtu/rag-quiz.git
cd rag-quiz

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and add HUGGINGFACEHUB_API_TOKEN
```

### Running Development Server

```bash
chainlit run app_c.py -w
```

Open `http://localhost:8000` and start developing!

### Code Quality

- **Type Hints**: 100% coverage
- **Logging**: 65+ debug points for tracing
- **Error Handling**: Centralized `handle_error()` function
- **Testing**: Import and configuration validation

### Key Modules

#### `app_c.py` - Main Application
- `load_pdf_files()` - Load PDFs into documents
- `perform_semantic_analysis()` - Semantic chunking
- `create_and_store_vectorstore()` - Create vector indices
- `refine_question()` - Improve queries with conversation context
- `handle_error()` - Centralized error handling
- `@cl.on_chat_start` / `@cl.on_message` / `@cl.on_chat_end` - Event handlers

#### `setup_core.py`
```python
init_llm()         # Returns ChatHuggingFace (Llama 3.1)
init_embeddings()  # Returns Sentence Transformers
```

#### `modules/file_handler.py`
```python
save_and_load_pdf(file, path)  # Upload and load PDFs
cleanup_folder(path)            # Clean session folders
```

#### `modules/rag_engine.py`
```python
split_documents(docs)                    # Semantic chunking
create_vectorstore(chunks, existing)     # FAISS indexing
get_hybrid_retriever(vectorstore, docs)  # BM25 + semantic search
```

### Performance Tips

- **Profiling**: Use `cProfile` to identify bottlenecks
- **Caching**: Consider caching embeddings model and vector indices
- **Async**: All I/O operations use `cl.make_async()` for non-blocking execution
- **Monitoring**: Track API rate limits (HF), memory (embeddings), response times

## 📚 Architecture

**RAG Pipeline**:
1. **Upload** → PDFs loaded via PyPDF
2. **Semantic Chunking** → Smart text splitting by topic
3. **Embeddings** → Multilingual Sentence Transformers
4. **Indexing** → FAISS vector store (semantic) + BM25 (keyword)
5. **Retrieval** → Hybrid search combining both approaches
6. **Generation** → Llama 3.1 via HuggingFace with source citations

**Session Management**:
- Per-user temporary folders in `temp_sessions/`
- Auto-cleanup on session end
- Conversation history for context-aware responses

**LLM Configuration** (setup_core.py):
- **Model**: Meta-Llama-3.1-8B-Instruct
- **Max Tokens**: 512
- **Temperature**: 0.01 (deterministic)
- **Timeout**: 120 seconds

**Retrieval Configuration** (modules/rag_engine.py):
- **Documents per Retriever**: 5
- **Max Combined Results**: 6
- **Chunking**: Semantic-based splitting