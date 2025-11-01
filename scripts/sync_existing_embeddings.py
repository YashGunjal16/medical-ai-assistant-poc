"""
Synchronize existing ChromaDB embeddings with checkpoint system.
Run this after uploading PDFs via browser to track progress.
Usage: python scripts/sync_existing_embeddings.py <pdf_path> <document_name>
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app.utils.logger import logger
from app.utils.pdf_processor import PDFProcessor
from app.utils.vector_store import VectorStore
from app.utils.checkpoint_manager import CheckpointManager
from dotenv import load_dotenv


def sync_embeddings_with_checkpoint(pdf_path: str, document_name: str):
    """
    Scan ChromaDB for existing embeddings and create checkpoint.
    This lets resume script know about embeddings created via browser upload.
    """
    
    if not os.path.exists(pdf_path):
        print(f"✗ Error: PDF not found at {pdf_path}")
        return False
    
    try:
        load_dotenv()
        
        # Initialize managers
        processor = PDFProcessor()
        vector_store = VectorStore()
        checkpoint_manager = CheckpointManager()
        
        print(f"\n📊 Syncing Embeddings for: {document_name}")
        print(f"📁 PDF: {pdf_path}")
        
        # Extract chunks from PDF
        print(f"\n🔄 Extracting chunks from PDF...")
        all_chunks = processor.process_pdf(pdf_path)
        print(f"✓ Total chunks in PDF: {len(all_chunks)}")
        
        # Create chunk ID set for comparison
        chunk_ids_in_pdf = {chunk[0] for chunk in all_chunks}
        
        # Get existing embeddings from ChromaDB
        print(f"\n📦 Scanning ChromaDB for existing embeddings...")
        stats = vector_store.get_stats()
        total_in_store = stats['total_documents']
        print(f"✓ Total documents in ChromaDB: {total_in_store}")
        
        # Query the collection to get all existing IDs
        # Get a sample to check if embeddings exist for this document
        try:
            # Try to get all documents from collection
            results = vector_store.collection.get(
                where={"source": {"$eq": f"pdf_upload_{os.path.basename(pdf_path)}"}}
            )
            existing_ids = set(results.get('ids', []))
        except:
            existing_ids = set()
        
        if not existing_ids:
            # If no matching source, try getting all IDs
            try:
                all_results = vector_store.collection.get()
                existing_ids = set(all_results.get('ids', []))
            except:
                existing_ids = set()
        
        # Find processed chunks (intersection of PDF chunks and ChromaDB)
        processed_ids = chunk_ids_in_pdf.intersection(existing_ids)
        
        print(f"\n✓ Found {len(processed_ids)} already embedded chunks")
        print(f"✓ Remaining to process: {len(chunk_ids_in_pdf) - len(processed_ids)}")
        
        # Create checkpoint
        checkpoint = {
            "processed_chunks": len(processed_ids),
            "total_chunks": len(all_chunks),
            "processed_ids": list(processed_ids),
            "document_name": document_name,
            "sync_timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        checkpoint_manager.save_checkpoint(document_name, checkpoint)
        
        print(f"\n✅ Checkpoint synchronized!")
        print(f"\n📈 Progress:")
        progress_pct = (len(processed_ids) / len(all_chunks) * 100) if all_chunks else 0
        print(f"  - Processed: {len(processed_ids)}/{len(all_chunks)} ({progress_pct:.1f}%)")
        print(f"  - Remaining: {len(chunk_ids_in_pdf) - len(processed_ids)}")
        print(f"\n💡 Next step: python scripts/resume_embeddings.py {pdf_path} {document_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error syncing embeddings: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 2:
        pdf_path = sys.argv[1]
        document_name = sys.argv[2]
        success = sync_embeddings_with_checkpoint(pdf_path, document_name)
    else:
        print("Usage: python scripts/sync_existing_embeddings.py <pdf_path> <document_name>")
        print("Example: python scripts/sync_existing_embeddings.py data/nephrology_reference.pdf nephrology")
        print("\nThis script:")
        print("  1. Extracts all chunks from the PDF")
        print("  2. Queries ChromaDB for existing embeddings")
        print("  3. Creates a checkpoint tracking what's been done")
        print("  4. Shows you resume progress for next run")
        success = False
    
    sys.exit(0 if success else 1)
