"""Check real ChromaDB embedding storage and vector retrieval."""
from rag.vector_store import initialize_index, retrieve_context

collection = initialize_index()
print("ChromaDB collection:", collection.name)
print("Stored knowledge documents:", collection.count())
question = "Calculate total sales for each restaurant."
print("Question:", question)
records = retrieve_context(collection, question, top_k=5)
for record in records:
    print(f"Retrieved: {record['id']} (distance={record['distance']:.3f})")
assert collection.count() == 10, "Expected 10 indexed documents"
assert len(records) == 5, "Vector search did not retrieve 5 records"
print("PASS: actual vector retrieval works")
