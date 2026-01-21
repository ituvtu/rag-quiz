import os
import shutil
import logging
from typing import List

import chainlit as cl
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


async def save_and_load_pdf(
    uploaded_file: cl.File,
    storage_path: str
) -> List[Document]:
    """Load PDF file and extract documents."""
    try:
        logging.info(f"Processing file: {uploaded_file.name}")
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
            logging.info(f"Created storage path: {storage_path}")

        destination_path = os.path.join(storage_path, uploaded_file.name)
        logging.info(f"Destination path: {destination_path}")
        
        if uploaded_file.content is not None:
            file_content = uploaded_file.content
            logging.info(f"File has content, size: {len(file_content) if hasattr(file_content, '__len__') else 'unknown'}")
            
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            with open(destination_path, "wb") as f:
                f.write(file_content)
            logging.info(f"Saved file to {destination_path}")
                
        elif uploaded_file.path:
            logging.info(f"File has path: {uploaded_file.path}")
            with open(destination_path, "wb") as dest:
                with open(str(uploaded_file.path), "rb") as src:
                    dest.write(src.read())
            logging.info(f"Copied file to {destination_path}")
        else:
            error_msg = f"File {uploaded_file.name} is empty (no content/path)"
            logging.error(error_msg)
            raise ValueError(error_msg)
        
        logging.info(f"Loading PDF from {destination_path}")
        pdf_loader = PyPDFLoader(destination_path)
        documents = await cl.make_async(pdf_loader.load)()
        logging.info(f"Loaded {len(documents)} pages from {uploaded_file.name}")
        
        for document in documents:
            document.metadata["source"] = str(destination_path)
            document.metadata["name"] = uploaded_file.name
            
        return documents
        
    except Exception as error:
        logging.error(f"Error in save_and_load_pdf for {uploaded_file.name}: {error}", exc_info=True)
        raise


def cleanup_folder(folder_path: str) -> None:
    """Remove folder and its contents."""
    if folder_path and os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"🗑️ [CLEANUP] Deleted: {folder_path}")
        except Exception as e:
            print(f"⚠️ Error deleting {folder_path}: {e}")