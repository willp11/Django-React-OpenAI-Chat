from chromadb.utils import embedding_functions
from django.conf import settings
from chat.client import create_openai_client

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


def query_rag(question, k=3):
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

    client = create_openai_client()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content
