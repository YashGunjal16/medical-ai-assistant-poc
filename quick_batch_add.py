# recover_embeddings.py
import sys
sys.path.insert(0, '.')

from app.utils.vector_store import VectorStore
from app.utils.pdf_processor import PDFProcessor
from app.utils.embeddings import EmbeddingsManager
from app.utils.checkpoint_manager import CheckpointManager
from dotenv import load_dotenv

load_dotenv()

print("🔄 Recovering embedding process...")

# Initialize
pdf_path = "app/data/nephrology_reference.pdf"
doc_name = "nephrology"

checkpoint_manager = CheckpointManager()
checkpoint = checkpoint_manager.load_checkpoint(doc_name)

if not checkpoint:
    print("❌ No checkpoint found")
    sys.exit(1)

print(f"📊 Checkpoint status: {checkpoint['processed_chunks']}/{checkpoint['total_chunks']}")

# Check what's already in ChromaDB
vector_store = VectorStore()
try:
    existing = vector_store.collection.get()
    existing_ids = set(existing['ids'])
    print(f"✓ Found {len(existing_ids)} existing embeddings in ChromaDB")
    
    # Count how many are from this document
    nephrology_ids = [id for id in existing_ids if id.startswith(doc_name)]
    print(f"✓ Found {len(nephrology_ids)} nephrology embeddings already")
    
    if len(nephrology_ids) > 0:
        print("\n✅ Embeddings are already in ChromaDB!")
        print(f"📈 Progress: {len(nephrology_ids)}/{checkpoint['total_chunks']}")
        
        # Update checkpoint
        checkpoint['processed_chunks'] = len(nephrology_ids)
        checkpoint['processed_ids'] = nephrology_ids
        checkpoint_manager.save_checkpoint(doc_name, checkpoint)
        print("✅ Checkpoint updated!")
    else:
        print("\n❌ No nephrology embeddings found in ChromaDB")
        print("Need to re-run the embedding process")
        
except Exception as e:
    print(f"❌ Error: {e}")