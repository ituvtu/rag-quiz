import os
import getpass
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage


def setup_environment():
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        print("Enter your Hugging Face Access Token (Write/Read):")
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = getpass.getpass()


def init_llm():
    model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    
    llm_endpoint = HuggingFaceEndpoint(
        model=model_id,
        max_new_tokens=512,
        do_sample=False, 
        temperature=0.01,
        repetition_penalty=1.1,
        timeout=120,
    )

    chat_model = ChatHuggingFace(llm=llm_endpoint)
    
    return chat_model


def init_embeddings():
    print("Loading embeddings model...")
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings


def test_connection(chat_model, embeddings):
    print("\n--- TEST 1: LLM (Chat Mode) ---")
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello! Write one short sentence about AI.")
        ]
        
        response = chat_model.invoke(messages)
        
        print(f"Request sent.")
        print(f"LLM Response:\n{response.content}")
    except Exception as e:
        print(f"LLM Error: {e}")

    print("\n--- TEST 2: Embeddings ---")
    try:
        text = "Test string for vectorization."
        vector = embeddings.embed_query(text)
        print(f"Text successfully converted to vector.")
        print(f"Vector dimension: {len(vector)}")
    except Exception as e:
        print(f"Embeddings Error: {e}")


if __name__ == "__main__":
    setup_environment()
    
    try:
        chat_model_instance = init_llm()
        embeddings_instance = init_embeddings()
        
        test_connection(chat_model_instance, embeddings_instance)
        
        print("\nSuccess! Core system configured.")
        
    except Exception as global_error:
        print(f"\nCritical initialization error: {global_error}")
