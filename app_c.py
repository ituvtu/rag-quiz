import logging
import os

noisy_libraries = [
    "chainlit", 
    "watchfiles", 
    "sentence_transformers", 
    "faiss",
    "httpcore",
    "httpx",
    "huggingface_hub"
]

for lib in noisy_libraries:
    logging.getLogger(lib).setLevel(logging.ERROR)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
import time
from typing import List, Any

import chainlit as cl
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.documents import Document

from setup_core import init_llm
from modules.file_handler import save_and_load_pdf, cleanup_folder
from modules.rag_engine import split_documents, create_vectorstore, get_hybrid_retriever
from modules.prompts import SYSTEM_REFINE_QUERY, get_answer_instruction

load_dotenv()

TEMP_SESSIONS_FOLDER = "temp_sessions"
CONVERSATION_HISTORY_MESSAGES = 3

if not os.path.exists(TEMP_SESSIONS_FOLDER):
    os.makedirs(TEMP_SESSIONS_FOLDER)


async def index_files_workflow(files: List[cl.File]):
    start_time = time.time()
    session_path = cl.user_session.get("session_folder")
    if not session_path: return

    async with cl.Step(name="Processing files", type="run") as step:
        step.input = f"🚀 Reading {len(files)} files..."
        await step.update()

        tasks = [save_and_load_pdf(f, session_path) for f in files]
        results = await asyncio.gather(*tasks)
        all_docs = [doc for res in results for doc in res]

        if not all_docs:
            step.output = "❌ Failed."
            return

        step.input = f"🧠 Semantic analysis ({len(all_docs)} pages)..."
        await step.update()
        new_chunks = await split_documents(all_docs)

        step.input = f"📊 Indexing ({len(new_chunks)} chunks)..."
        await step.update()
        
        vector_store = cl.user_session.get("vectorstore")
        all_splits: List[Document] = cl.user_session.get("all_splits") or []
        
        vector_store = await create_vectorstore(new_chunks, vector_store)
        all_splits.extend(new_chunks)
        
        retriever = get_hybrid_retriever(vector_store, all_splits)
        
        cl.user_session.set("vectorstore", vector_store)
        cl.user_session.set("all_splits", all_splits)
        cl.user_session.set("retriever", retriever)

        elapsed = time.time() - start_time
        step.output = f"✅ Done ({elapsed:.1f}s)"
    
    await cl.Message(content=f"✅ Ready! ({elapsed:.1f}s)").send()


async def refine_question(llm, question: str, history: List):
    if not history: return question
    
    recent = history[-CONVERSATION_HISTORY_MESSAGES:]
    hist_text = "\n".join([f"{r}: {t}" for r, t in recent])
    
    res = await cl.make_async(llm.invoke)([
        SystemMessage(content=SYSTEM_REFINE_QUERY),
        HumanMessage(content=f"History:\n{hist_text}\n\nQuestion: {question}")
    ])
    return res.content if isinstance(res.content, str) else question


def get_sources_elements(docs: List[Document]):
    names, elements, seen = [], [], set()
    for d in docs:
        src = d.metadata.get("source")
        name = d.metadata.get("name", "Doc")
        page = d.metadata.get("page", 0) + 1
        key = (name, page)
        
        if key not in seen and src and os.path.exists(src):
            lbl = f"{name} (p. {page})"
            elements.append(cl.Pdf(name=lbl, display="side", path=src, page=page))
            names.append(lbl)
            seen.add(key)
    return names, elements


@cl.on_chat_start
async def start():
    cl.user_session.set("vectorstore", None)
    cl.user_session.set("all_splits", [])
    cl.user_session.set("history", [])
    
    s_id = cl.user_session.get("id")
    if s_id:
        s_path = os.path.join(TEMP_SESSIONS_FOLDER, str(s_id))
        if not os.path.exists(s_path): os.makedirs(s_path)
        cl.user_session.set("session_folder", s_path)

    await cl.Message(content="Hi! 👋 Upload PDFs to start.").send()


@cl.on_chat_end
def end():
    path = cl.user_session.get("session_folder")
    if path:
        cleanup_folder(str(path))


@cl.on_message
async def main(message: cl.Message):
    pdfs: List[Any] = [f for f in (message.elements or []) if hasattr(f, 'mime') and f.mime and "pdf" in f.mime]
    if pdfs:
        await index_files_workflow(pdfs)
    
    if not message.content: return

    retriever = cl.user_session.get("retriever")
    if not retriever:
        await cl.Message(content="⚠️ Upload files first!").send()
        return

    llm = init_llm()
    history: List[Any] = cl.user_session.get("history") or []
    
    refined_q = await refine_question(llm, message.content, history)
    
    docs = await cl.make_async(retriever.invoke)(refined_q)
    context = "\n".join([d.page_content for d in docs])
    
    prompt = get_answer_instruction(context, message.content)
    msg = cl.Message(content="")
    await msg.send()
    
    full_resp = ""
    async for chunk in llm.astream([
        SystemMessage(content=prompt),
        HumanMessage(content=message.content)
    ]):
        if isinstance(chunk.content, str):
            token = chunk.content
            full_resp += token
            await msg.stream_token(token)
            
    names, elements = get_sources_elements(docs)
    if names:
        msg.content += "\n\n**📚 Sources:**\n" + "\n".join([f"* {n}" for n in names])
        full_resp += "\n\n**📚 Sources:**..."
    
    msg.elements = elements
    await msg.update()
    
    if history is None: history = []
    history.append(("user", message.content))
    history.append(("assistant", full_resp))
    cl.user_session.set("history", history)
