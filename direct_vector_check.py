# direct_vector_check.py
from app.utils.vector_store import VectorStore

vs = VectorStore(persist_dir="app/vectorstore/chroma")

# Get raw collection data
collection = vs.collection
total = collection.count()

print(f"Total embeddings in collection: {total}")

# Get ALL IDs
if total < 1000:
    all_data = collection.get()
    print(f"\nAll IDs ({len(all_data['ids'])}):")
    for i, id in enumerate(all_data['ids'][:50]):
        print(f"  {i+1}. {id}")
else:
    # Get in batches
    print(f"\nToo many to display all. First 50:")
    sample = collection.get(limit=50)
    for i, id in enumerate(sample['ids']):
        print(f"  {i+1}. {id}")