"""Smoke test: real ChromaDB storage + similarity retrieval."""
from rag.vector_store import initialize_index, retrieve_context

collection = initialize_index()
print("ChromaDB collection:", collection.name)
print("Stored knowledge documents:", collection.count())
question = "Calculate total sales for each restaurant"
print("Query:", question)
results = retrieve_context(collection, question, top_k=5)
for row in results:
    print(f"Retrieved: {row['id']} (distance={row['distance']:.3f})")
assert collection.count() >= 10, "Not all knowledge documents were stored"
assert len(results) == 5, "Similarity search returned an unexpected number of results"
print("PASS: real vector retrieval works")
