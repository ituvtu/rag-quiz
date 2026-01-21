from typing import List, Any, Optional

import chainlit as cl
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

from setup_core import init_embeddings
import logging

DOCUMENTS_PER_RETRIEVER = 5 
MAX_COMBINED_DOCUMENTS = 6     


class SimpleEnsembleRetriever(BaseRetriever):
    """Ensemble retriever combining multiple retrieval strategies."""
    retrievers: List[BaseRetriever]
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[Any] = None
    ) -> List[Document]:
        """Get combined results from all retrievers."""
        results_lists = [r.invoke(query) for r in self.retrievers]
        combined_docs: List[Document] = []
        doc_ids: set = set()
        
        max_len = max(len(r) for r in results_lists)
        for i in range(max_len):
            for r_list in results_lists:
                if i < len(r_list):
                    doc = r_list[i]
                    if doc.page_content not in doc_ids:
                        combined_docs.append(doc)
                        doc_ids.add(doc.page_content)
                        if len(combined_docs) >= MAX_COMBINED_DOCUMENTS:
                            return combined_docs
        return combined_docs


async def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into semantic chunks."""
    logging.info("Initializing embeddings model for chunking...")
    embeddings_model = init_embeddings()
    logging.info("Creating semantic chunker...")
    chunker = SemanticChunker(embeddings_model, breakpoint_threshold_type="percentile")
    logging.info(f"Splitting {len(documents)} documents...")
    result = await cl.make_async(chunker.split_documents)(documents)
    logging.info(f"Split into {len(result)} chunks")
    return result


async def create_vectorstore(
    chunks: List[Document],
    existing_store: Optional[FAISS] = None
) -> FAISS:
    """Create or update FAISS vectorstore."""
    logging.info("Initializing embeddings model for vectorstore...")
    embeddings_model = init_embeddings()
    if existing_store is None:
        logging.info(f"Creating new FAISS vectorstore with {len(chunks)} chunks...")
        result = await cl.make_async(FAISS.from_documents)(chunks, embeddings_model)
        logging.info("FAISS vectorstore created successfully")
        return result
    else:
        logging.info(f"Adding {len(chunks)} chunks to existing vectorstore...")
        await cl.make_async(existing_store.add_documents)(chunks)
        logging.info("Chunks added to existing vectorstore")
        return existing_store


def get_hybrid_retriever(
    vector_store: FAISS,
    all_chunks: List[Document]
) -> SimpleEnsembleRetriever:
    """Create hybrid retriever combining FAISS and BM25."""
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": DOCUMENTS_PER_RETRIEVER})
    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = DOCUMENTS_PER_RETRIEVER
    
    return SimpleEnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever])
