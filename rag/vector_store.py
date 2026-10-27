"""Actual ChromaDB vector retrieval (not a hard-coded context lookup)."""
from pathlib import Path

from rag.knowledge import documents

COLLECTION_NAME = "restaurant_sql_knowledge_v1"


def initialize_index(path=None):
    """Build an on-disk Chroma collection and embed/upsert the knowledge.

    Chroma's default ONNX embedding model may download on first use. This can
    take a little longer on a new computer or after a cloud deployment restart.
    The index is rebuilt if the ephemeral cloud storage is lost.
    """
    import chromadb

    directory = Path(path) if path else Path(__file__).resolve().parents[1] / ".chroma"
    directory.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(directory))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    rows = documents()
    # Upsert also refreshes docs when the project is updated.
    collection.upsert(
        ids=[item[0] for item in rows],
        documents=[item[1] for item in rows],
        metadatas=[item[2] for item in rows],
    )
    return collection


def retrieve_context(collection, question: str, top_k: int = 5):
    """Perform a real similarity search over stored vector embeddings."""
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Please enter a question.")
    count = collection.count()
    if count == 0:
        raise ValueError("The knowledge collection is empty.")
    response = collection.query(
        query_texts=[question.strip()],
        n_results=min(max(1, top_k), count),
        include=["documents", "distances", "metadatas"],
    )
    result = []
    for doc_id, body, distance in zip(
        response["ids"][0], response["documents"][0], response["distances"][0]
    ):
        result.append({"id": doc_id, "text": body, "distance": float(distance)})
    return result
