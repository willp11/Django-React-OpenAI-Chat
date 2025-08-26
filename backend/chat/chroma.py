from chromadb.utils import embedding_functions
from django.conf import settings

import chromadb
import tiktoken

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name="text-embedding-3-small"
)

collection = chroma_client.get_or_create_collection(
    name="personal_knowledge",
    embedding_function=openai_ef
)

def chunk_text(text, max_tokens=500, overlap=50):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens - overlap):
        chunk = enc.decode(tokens[i:i+max_tokens])
        chunks.append(chunk)
    return chunks


def load_documents(documents: list[str]):
    for i, doc in enumerate(documents):
        chunks = chunk_text(doc)
        for j, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                ids=[f"doc_{i}_chunk_{j}"],
                metadatas=[{"source": f"doc_{i}"}]
            )


def create_rag_prompt(question, previous_messages, k=3):
    if previous_messages:
        previous_messages_text = "\n".join([f'{message.message}: {message.content}' for message in previous_messages])
        question = f'{previous_messages_text}\n{question}'

    results = collection.query(
        query_texts=[question],
        n_results=k
    )
    
    retrieved_docs = results["documents"][0]
    context = "\n".join(retrieved_docs)

    prompt = f"""You are a chatbot that answers questions about me.
    Question: {question}
    Context: {context}
    Answer: reply to the question based on the context.
    """

    return prompt
