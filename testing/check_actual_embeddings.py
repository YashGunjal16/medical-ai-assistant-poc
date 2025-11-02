# check_actual_embeddings.py
import chromadb
import os

# Check the main collection
db_path = "app/vectorstore/chroma"
client = chromadb.PersistentClient(path=db_path)

print("=" * 60)
print("CHROMADB ANALYSIS")
print("=" * 60)

# List all collections
collections = client.list_collections()
print(f"\n📚 Collections found: {len(collections)}")

for coll in collections:
    print(f"\n📁 Collection: '{coll.name}'")
    count = coll.count()
    print(f"   Total documents: {count}")
    
    # Get all IDs (or first 100 if too many)
    try:
        all_data = coll.get(limit=min(count, 100))
        print(f"   Sample IDs (first 10):")
        for i, id in enumerate(all_data['ids'][:10]):
            print(f"      {i+1}. {id}")
        
        # Check metadata
        if all_data['metadatas']:
            print(f"\n   Sample Metadata:")
            unique_sources = set()
            for meta in all_data['metadatas'][:20]:
                if meta and 'source' in meta:
                    unique_sources.add(meta['source'])
            for source in list(unique_sources)[:5]:
                print(f"      - {source}")
    
    except Exception as e:
        print(f"   Error reading collection: {e}")

# Check actual file sizes
print("\n" + "=" * 60)
print("FILE SYSTEM CHECK")
print("=" * 60)
for root, dirs, files in os.walk(db_path):
    for file in files:
        filepath = os.path.join(root, file)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > 0.1:  # Only show files > 0.1 MB
            print(f"📄 {file}: {size_mb:.2f} MB")