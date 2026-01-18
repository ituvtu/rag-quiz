from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace, HuggingFaceEmbeddings

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
    model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings
