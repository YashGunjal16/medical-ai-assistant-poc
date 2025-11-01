# check_collections.py
import chromadb

client = chromadb.PersistentClient(path="app/vectorstore/chroma")

# List all collections
collections = client.list_collections()
print(f"Found {len(collections)} collection(s):\n")

for coll in collections:
    print(f"📁 Collection: {coll.name}")
    count = coll.count()
    print(f"   Documents: {count}")
    
    # Get sample IDs
    if count > 0:
        sample = coll.get(limit=5)
        print(f"   Sample IDs: {sample['ids'][:3]}")
    print()