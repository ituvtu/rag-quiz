import asyncio
import logging
import os
import time
from typing import List, Any, Optional, Tuple

import chainlit as cl
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from modules.file_handler import cleanup_folder, save_and_load_pdf
from modules.prompts import SYSTEM_REFINE_QUERY, get_answer_instruction
from modules.rag_engine import create_vectorstore, get_hybrid_retriever, split_documents
from setup_core import init_llm

# Load environment variables before any other configuration
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)

logger = logging.getLogger(__name__)

# Configure noisy library logging
noisy_libraries = [
    "chainlit",
    "watchfiles",
    "sentence_transformers",
    "faiss",
    "httpcore",
    "httpx",
    "huggingface_hub",
]

for lib in noisy_libraries:
    logging.getLogger(lib).setLevel(logging.ERROR)

# Environment variables and configuration
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Configuration Settings
class Config:
    """Application configuration from environment variables."""
    
    # Session management
    TEMP_SESSIONS_FOLDER: str = os.getenv("TEMP_SESSIONS_FOLDER", "temp_sessions")
    
    # Conversation settings
    CONVERSATION_HISTORY_MESSAGES: int = int(os.getenv("CONVERSATION_HISTORY_MESSAGES", "3"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Optional: Document processing settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_FILE_TYPES: str = os.getenv("ALLOWED_FILE_TYPES", "pdf")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration settings."""
        try:
            # Check if temp sessions folder can be created
            if not os.path.exists(cls.TEMP_SESSIONS_FOLDER):
                os.makedirs(cls.TEMP_SESSIONS_FOLDER)
                logger.info(f"Created temp sessions folder: {cls.TEMP_SESSIONS_FOLDER}")
            
            logger.debug(f"Configuration validated: TEMP_SESSIONS_FOLDER={cls.TEMP_SESSIONS_FOLDER}, "
                        f"CONVERSATION_HISTORY_MESSAGES={cls.CONVERSATION_HISTORY_MESSAGES}, "
                        f"MAX_FILE_SIZE_MB={cls.MAX_FILE_SIZE_MB}")
            return True
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}", exc_info=e)
            return False

# Validate configuration on startup
if not Config.validate():
    logger.error("Failed to validate application configuration")
else:
    logger.info("✅ Application configuration validated successfully")
    logger.info(f"📂 Session folder: {Config.TEMP_SESSIONS_FOLDER}")
    logger.info("🚀 Application ready to start - models will be loaded on first use")

# Create convenient aliases for backward compatibility
TEMP_SESSIONS_FOLDER = Config.TEMP_SESSIONS_FOLDER
CONVERSATION_HISTORY_MESSAGES = Config.CONVERSATION_HISTORY_MESSAGES


class AppError(Exception):
    """Base application error class."""
    pass


async def handle_error(
    error: BaseException,
    error_msg: str,
    step: Optional[cl.Step] = None,
    send_message: bool = True
) -> None:
    """
    Centralized error handling.
    
    Args:
        error: The exception that occurred
        error_msg: User-friendly error message
        step: Optional Chainlit Step to update
        send_message: Whether to send message to user
    """
    logger.error(error_msg, exc_info=error)
    
    if step is not None:
        step.output = f"❌ {error_msg}"
    
    if send_message:
        try:
            await cl.Message(content=f"⚠️ {error_msg}").send()
        except Exception as msg_error:
            logger.error(f"Failed to send error message: {str(msg_error)}")


async def load_pdf_files(
    files: List[cl.File],
    session_path: str,
    step: cl.Step
) -> List[Document]:
    """Load and process PDF files into documents."""
    logger.debug(f"load_pdf_files called with {len(files)} files, session_path={session_path}")
    step.input = f"🚀 Reading {len(files)} files..."
    await step.update()
    logger.info(f"Starting to process {len(files)} files from session {session_path}")

    try:
        tasks = [save_and_load_pdf(f, session_path) for f in files]
        logger.debug(f"Created {len(tasks)} async tasks for PDF loading")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_docs: List[Document] = []
        for i, result in enumerate(results):
            file_name = files[i].name if i < len(files) else "unknown"
            if isinstance(result, BaseException):
                error_msg = f"Error loading file '{file_name}': {str(result)}"
                await handle_error(result, error_msg, step, send_message=False)
                raise ValueError(error_msg)
            elif isinstance(result, list):
                logger.debug(f"File '{file_name}' loaded successfully with {len(result)} documents")
                all_docs.extend(result)
            else:
                logger.warning(f"Unexpected result type for file '{file_name}': {type(result)}")
        
        logger.info(f"PDF loading completed: {len(all_docs)} documents extracted from {len(files)} files")
        
        if not all_docs:
            error_msg = "No documents loaded from PDF files"
            await handle_error(AppError(error_msg), error_msg, step, send_message=False)
            raise ValueError(error_msg)
        
        logger.debug(f"Returning {len(all_docs)} documents from load_pdf_files")
        return all_docs
    except Exception as e:
        if not isinstance(e, ValueError):
            await handle_error(e, f"Unexpected error in load_pdf_files: {str(e)}", step, send_message=False)
        raise


async def perform_semantic_analysis(
    all_docs: List[Document],
    step: cl.Step
) -> List[Document]:
    """Perform semantic chunking on documents."""
    logger.debug(f"perform_semantic_analysis called with {len(all_docs)} documents")
    step.input = f"🧠 Semantic analysis ({len(all_docs)} pages)..."
    await step.update()
    logger.info(f"Starting semantic chunking on {len(all_docs)} documents")
    
    start_time = time.time()
    try:
        new_chunks = await split_documents(all_docs)
        elapsed = time.time() - start_time
        logger.info(f"Semantic analysis completed in {elapsed:.2f}s: {len(new_chunks)} chunks created from {len(all_docs)} documents")
        logger.debug(f"Average chunk size: {len(all_docs) / len(new_chunks) if new_chunks else 0:.2f} docs per chunk")
        return new_chunks
    except Exception as e:
        error_msg = f"Error during semantic analysis: {str(e)}"
        await handle_error(e, error_msg, step, send_message=False)
        raise


async def create_and_store_vectorstore(
    new_chunks: List[Document],
    step: cl.Step
) -> Tuple[Any, Any]:
    """Create vectorstore and retriever, and store in session."""
    logger.debug(f"create_and_store_vectorstore called with {len(new_chunks)} chunks")
    step.input = f"📊 Indexing ({len(new_chunks)} chunks)..."
    await step.update()
    logger.info(f"Starting vectorstore creation with {len(new_chunks)} new chunks")
    
    vector_store = cl.user_session.get("vectorstore")
    all_splits: List[Document] = cl.user_session.get("all_splits") or []
    logger.debug(f"Retrieved existing vectorstore: {vector_store is not None}, existing splits: {len(all_splits)}")
    
    start_time = time.time()
    try:
        vector_store = await create_vectorstore(new_chunks, vector_store)
        elapsed = time.time() - start_time
        logger.info(f"Vectorstore created successfully in {elapsed:.2f}s")
    except Exception as e:
        error_msg = f"Error creating vectorstore: {str(e)}"
        await handle_error(e, error_msg, step, send_message=False)
        raise
    
    all_splits.extend(new_chunks)
    logger.debug(f"Extended splits collection: now contains {len(all_splits)} documents")
    
    try:
        retriever = get_hybrid_retriever(vector_store, all_splits)
        logger.info(f"Hybrid retriever created successfully for {len(all_splits)} documents")
    except Exception as e:
        error_msg = f"Error creating retriever: {str(e)}"
        await handle_error(e, error_msg, step, send_message=False)
        raise
    
    cl.user_session.set("vectorstore", vector_store)
    cl.user_session.set("all_splits", all_splits)
    cl.user_session.set("retriever", retriever)
    logger.debug("Session data updated with vectorstore, splits, and retriever")
    
    return vector_store, retriever


async def index_files_workflow(files: List[cl.File]):
    """Main workflow for indexing PDF files."""
    logger.debug(f"index_files_workflow called with {len(files)} files")
    start_time = time.time()
    session_path = cl.user_session.get("session_folder")
    if not session_path:
        error_msg = "No session folder found"
        logger.error(error_msg)
        return

    logger.info(f"Starting file indexing workflow for {len(files)} file(s) in session {session_path}")
    try:
        async with cl.Step(name="Processing files", type="run") as step:
            try:
                logger.debug("Loading PDF files...")
                all_docs = await load_pdf_files(files, session_path, step)
                
                logger.debug("Performing semantic analysis...")
                new_chunks = await perform_semantic_analysis(all_docs, step)
                
                logger.debug("Creating and storing vectorstore...")
                await create_and_store_vectorstore(new_chunks, step)
                
                elapsed = time.time() - start_time
                step.output = f"✅ Done ({elapsed:.1f}s)"
                logger.info(f"File indexing workflow completed successfully in {elapsed:.2f}s")
                await cl.Message(content=f"✅ Ready! ({elapsed:.1f}s)").send()
            except ValueError as e:
                logger.warning(f"Validation error in indexing workflow: {str(e)}")
                step.output = f"❌ {str(e)}"
                try:
                    await cl.Message(content=f"⚠️ {str(e)}").send()
                except Exception as msg_error:
                    logger.error(f"Failed to send validation error message: {str(msg_error)}")
            except Exception as e:
                error_msg = f"Unexpected error during indexing: {str(e)}"
                await handle_error(e, error_msg, step, send_message=False)
    except Exception as e:
        error_msg = f"Unexpected error in index_files_workflow: {str(e)}"
        await handle_error(e, error_msg, send_message=True)


async def refine_question(
    llm: Any,
    question: str,
    history: List[Tuple[str, str]]
) -> str:
    """Refine user question based on conversation history."""
    logger.debug(f"refine_question called with question length={len(question)}, history length={len(history)}")
    if not history:
        logger.debug("No conversation history available, returning original question")
        return question
    
    recent = history[-Config.CONVERSATION_HISTORY_MESSAGES:]
    logger.debug(f"Using {len(recent)} recent messages from history for question refinement")
    hist_text = "\n".join([f"{r}: {t}" for r, t in recent])
    
    try:
        res = await cl.make_async(llm.invoke)([
            SystemMessage(content=SYSTEM_REFINE_QUERY),
            HumanMessage(content=f"History:\n{hist_text}\n\nQuestion: {question}")
        ])
        refined = res.content if isinstance(res.content, str) else question
        logger.debug(f"Question refinement completed. Original length={len(question)}, refined length={len(refined)}")
        return refined
    except Exception as e:
        logger.warning(f"Error refining question, returning original: {str(e)}")
        return question


def get_sources_elements(docs: List[Document]) -> Tuple[List[str], List[Any]]:
    """Extract source documents and create displayable elements."""
    logger.debug(f"get_sources_elements called with {len(docs)} documents")
    names, elements, seen = [], [], set()
    
    for i, d in enumerate(docs):
        src = d.metadata.get("source")
        name = d.metadata.get("name", "Doc")
        page = d.metadata.get("page", 0) + 1
        key = (name, page)
        
        if key not in seen and src and os.path.exists(src):
            lbl = f"{name} (p. {page})"
            elements.append(cl.Pdf(name=lbl, display="side", path=src, page=page))
            names.append(lbl)
            seen.add(key)
            logger.debug(f"Added source element: {lbl}")
        elif key in seen:
            logger.debug(f"Skipping duplicate source: {name} page {page}")
        elif not src:
            logger.debug(f"Document {i} has no source metadata")
        elif not os.path.exists(src):
            logger.warning(f"Source path not found for {name}: {src}")
    
    logger.debug(f"Source extraction completed: {len(names)} unique sources found")
    return names, elements


@cl.on_chat_start
async def start():
    """Initialize chat session."""
    try:
        s_id = cl.user_session.get("id")
        logger.info(f"Chat session started: session_id={s_id}")
        
        cl.user_session.set("vectorstore", None)
        cl.user_session.set("all_splits", [])
        cl.user_session.set("history", [])
        logger.debug("Session data initialized: vectorstore=None, splits=[], history=[]")
        
        if s_id:
            s_path = os.path.join(TEMP_SESSIONS_FOLDER, str(s_id))
            if not os.path.exists(s_path):
                os.makedirs(s_path)
                logger.debug(f"Created session folder: {s_path}")
            else:
                logger.debug(f"Using existing session folder: {s_path}")
            cl.user_session.set("session_folder", s_path)
        else:
            logger.warning("No session ID found during initialization")

        await cl.Message(content="Hi! 👋 Upload PDFs to start.").send()
        logger.info("Initialization completed successfully")
    except Exception as e:
        error_msg = "Error in session initialization"
        await handle_error(e, error_msg, send_message=True)


@cl.on_chat_end
def end() -> None:
    """Clean up session resources."""
    s_id = cl.user_session.get("id")
    path = cl.user_session.get("session_folder")
    logger.info(f"Chat session ended: session_id={s_id}")
    if path:
        logger.debug(f"Cleaning up session folder: {path}")
        cleanup_folder(str(path))
        logger.debug("Session cleanup completed")
    else:
        logger.debug("No session folder to clean up")


@cl.on_message
async def main(message: cl.Message) -> None:
    """Handle incoming chat messages."""
    msg_id = getattr(message, 'id', 'unknown')
    logger.debug(f"Message received: msg_id={msg_id}, content_length={len(message.content) if message.content else 0}, elements={len(message.elements or [])}")
    
    try:
        pdfs: List[Any] = [f for f in (message.elements or []) if hasattr(f, 'mime') and f.mime and "pdf" in f.mime]
        if pdfs:
            logger.info(f"PDF files detected in message: {len(pdfs)} file(s)")
            await index_files_workflow(pdfs)
        
        if not message.content:
            logger.debug("Message has no text content, skipping processing")
            return

        logger.debug("Retrieving vectorstore and retriever from session")
        retriever = cl.user_session.get("retriever")
        if not retriever:
            logger.warning(f"No retriever available for message {msg_id}")
            await cl.Message(content="⚠️ Upload files first!").send()
            return

        logger.debug(f"Processing message: '{message.content[:50]}...'")
        llm = init_llm()
        history: List[Tuple[str, str]] = cl.user_session.get("history") or []
        
        refined_q = await refine_question(llm, message.content, history)
        logger.debug("Retrieving documents using hybrid retriever")
        
        docs = await cl.make_async(retriever.invoke)(refined_q)
        logger.debug(f"Retrieved {len(docs)} relevant documents")
        context = "\n".join([d.page_content for d in docs])
        
        prompt = get_answer_instruction(context, message.content)
        msg = cl.Message(content="")
        await msg.send()
        logger.debug("Starting LLM response streaming")
        
        full_resp = ""
        async for chunk in llm.astream([
            SystemMessage(content=prompt),
            HumanMessage(content=message.content)
        ]):
            if isinstance(chunk.content, str):
                token = chunk.content
                full_resp += token
                await msg.stream_token(token)
        
        logger.debug(f"LLM response completed: {len(full_resp)} characters")
        names, elements = get_sources_elements(docs)
        if names:
            msg.content += "\n\n**📚 Sources:**\n" + "\n".join([f"* {n}" for n in names])
            full_resp += "\n\n**📚 Sources:**..."
        
        msg.elements = elements
        await msg.update()
        
        if history is None:
            history = []
        history.append(("user", message.content))
        history.append(("assistant", full_resp))
        cl.user_session.set("history", history)
        logger.debug(f"Message processing completed. History length: {len(history)}")
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        await handle_error(e, error_msg, send_message=True)
