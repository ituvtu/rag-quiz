import os
import shutil
import chainlit as cl
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from typing import List

async def save_and_load_pdf(uploaded_file: cl.File, storage_path: str) -> List[Document]:
    try:
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)

        destination_path = os.path.join(storage_path, uploaded_file.name)
        
        if uploaded_file.content is not None:
            file_content = uploaded_file.content
            
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            with open(destination_path, "wb") as f:
                f.write(file_content)
                
        elif uploaded_file.path:
            with open(destination_path, "wb") as dest:
                with open(str(uploaded_file.path), "rb") as src:
                    dest.write(src.read())
        else:
            print(f"❌ Error: File {uploaded_file.name} is empty (no content/path).")
            return []
        
        pdf_loader = PyPDFLoader(destination_path)
        documents = await cl.make_async(pdf_loader.load)()
        
        for document in documents:
            document.metadata["source"] = str(destination_path)
            document.metadata["name"] = uploaded_file.name
            
        return documents
        
    except Exception as error:
        print(f"❌ Error inside save_and_load_pdf: {error}")
        return []

def cleanup_folder(folder_path: str):
    if folder_path and os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"🗑️ [CLEANUP] Deleted: {folder_path}")
        except Exception as e:
            print(f"⚠️ Error deleting {folder_path}: {e}")