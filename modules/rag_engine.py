from typing import List, Any
import chainlit as cl
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from setup_core import init_embeddings

DOCUMENTS_PER_RETRIEVER = 5 
MAX_COMBINED_DOCUMENTS = 6     


class SimpleEnsembleRetriever(BaseRetriever):
    retrievers: list
    
    def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> List[Document]:
        results_lists = [r.invoke(query) for r in self.retrievers]
        combined_docs = []
        doc_ids = set()
        
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
    embeddings_model = init_embeddings()
    chunker = SemanticChunker(embeddings_model, breakpoint_threshold_type="percentile")
    return await cl.make_async(chunker.split_documents)(documents)


async def create_vectorstore(chunks: List[Document], existing_store=None):
    embeddings_model = init_embeddings()
    if existing_store is None:
        return await cl.make_async(FAISS.from_documents)(chunks, embeddings_model)
    else:
        await cl.make_async(existing_store.add_documents)(chunks)
        return existing_store


def get_hybrid_retriever(vector_store, all_chunks: List[Document]) -> BaseRetriever:
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": DOCUMENTS_PER_RETRIEVER})
    bm25_retriever = BM25Retriever.from_documents(all_chunks)
    bm25_retriever.k = DOCUMENTS_PER_RETRIEVER
    
    return SimpleEnsembleRetriever(retrievers=[bm25_retriever, faiss_retriever])
