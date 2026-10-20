"""RAG helpers using LangChain, Azure OpenAI embeddings, and PostgreSQL/pgvector.

Vector RAG activates only when Azure OpenAI and VECTOR_CONNECTION are configured.
The API remains runnable locally without cloud credentials.
"""
from app.config import settings

COLLECTION = "pipelinepulse_knowledge"

def rag_is_configured() -> bool:
    return bool(
        settings.azure_openai_endpoint and settings.azure_openai_api_key
        and settings.azure_openai_embedding_deployment and settings.vector_connection
    )

def _components():
    from langchain_openai import AzureOpenAIEmbeddings
    from langchain_postgres import PGVector
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_deployment=settings.azure_openai_embedding_deployment,
    )
    store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION,
        connection=settings.vector_connection,
        use_jsonb=True,
    )
    return embeddings, store

def add_knowledge(text: str, metadata: dict) -> str:
    _, store = _components()
    ids = store.add_texts([text], metadatas=[metadata])
    return ids[0]

def retrieve_context(query: str, k: int = 4) -> list[dict]:
    _, store = _components()
    docs = store.similarity_search_with_score(query, k=k)
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "distance": float(score)}
        for doc, score in docs
    ]
