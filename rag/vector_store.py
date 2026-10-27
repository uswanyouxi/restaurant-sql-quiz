"""Persistent ChromaDB index and actual vector similarity retrieval."""
from pathlib import Path
from rag.knowledge import documents

COLLECTION_NAME = "restaurant_sql_knowledge_v1"


def initialize_index(path=None):
    import chromadb

    folder = Path(path) if path else Path(__file__).resolve().parents[1] / ".chroma"
    folder.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(folder))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    data = documents()
    # Chroma embeds and stores each document; the on-disk index may be
    # recreated on Streamlit Cloud when ephemeral storage is cleared.
    collection.upsert(
        ids=[item[0] for item in data],
        documents=[item[1] for item in data],
        metadatas=[item[2] for item in data],
    )
    return collection


def retrieve_context(collection, question, top_k=5):
    """Vector query: returns real Chroma IDs, distances and retrieved text."""
    if not question or not question.strip():
        raise ValueError("Please enter a natural-language question.")
    count = collection.count()
    if not count:
        raise ValueError("Vector database contains no knowledge.")
    response = collection.query(
        query_texts=[question.strip()],
        n_results=min(max(1, top_k), count),
        include=["documents", "distances"],
    )
    return [
        {"id": identifier, "text": text, "distance": float(distance)}
        for identifier, text, distance in zip(
            response["ids"][0],
            response["documents"][0],
            response["distances"][0],
        )
    ]
