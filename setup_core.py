from typing import Any

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings
import logging
import os


def init_llm() -> ChatHuggingFace:
    """Initialize and configure the HuggingFace LLM."""
    model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    logging.info(f"Initializing LLM: {model_id}")
    
    # Перевіряємо наявність токена
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")
    if not token:
        logging.warning("No HuggingFace token found in environment variables")
    else:
        logging.info(f"HuggingFace token found (length: {len(token)})")
    
    llm_endpoint = HuggingFaceEndpoint(
        model=model_id,
        max_new_tokens=512,
        do_sample=False, 
        temperature=0.01,
        repetition_penalty=1.1,
        timeout=120,
    )

    chat_model = ChatHuggingFace(llm=llm_endpoint)
    logging.info("LLM initialized successfully")
    
    return chat_model


def init_embeddings() -> HuggingFaceEmbeddings:
    """Initialize embeddings model for semantic search."""
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    logging.info(f"Initializing embeddings model: {model_name}")
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logging.info("Embeddings model initialized successfully")
        return embeddings
    except Exception as e:
        logging.error(f"Error initializing embeddings: {e}", exc_info=True)
        raise
