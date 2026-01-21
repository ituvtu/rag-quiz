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

### Try Online (No Setup Required)

Deploy to **Hugging Face Spaces** in 5 minutes:
1. Click "Create Space" on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Add `HUGGINGFACEHUB_API_TOKEN` as a secret
3. Push this repo to your Space

📖 **Detailed guide**: See [DEPLOY_HF_SPACES.md](DEPLOY_HF_SPACES.md)

### Prerequisites

- Python 3.10 or higher
- Hugging Face API token ([Get one here](https://huggingface.co/settings/tokens))

### Installation

#### Option A: Docker (Recommended for production)

1. Clone the repository:
```bash
git clone https://github.com/ituvtu/rag-quiz.git
cd rag-quiz
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your HUGGINGFACEHUB_API_TOKEN
```

3. Deploy with Docker Compose:
```bash
docker-compose up -d
```

Open `http://localhost:8000` in your browser.

#### Option B: Local Development

1. Clone the repository:
```bash
git clone https://github.com/ituvtu/rag-quiz.git
cd rag-quiz
```

2. Create and activate virtual environment:
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

**Docker:**
```bash
docker-compose up
```

**Local:**
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

### LLM Settings (setup_core.py)

- **Model**: `meta-llama/Meta-Llama-3.1-8B-Instruct`
- **Max Tokens**: 512
- **Temperature**: 0.01 (deterministic)
- **Timeout**: 120 seconds

### Retrieval Settings (modules/rag_engine.py)

- **Documents per Retriever**: 5
- **Max Combined Results**: 6
- **Chunking**: Semantic-based (percentile threshold)