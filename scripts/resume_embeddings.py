"""
Script to resume embedding process from last checkpoint.
Useful when embedding is interrupted - picks up from where it left off.
Usage: python scripts/resume_embeddings.py
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
import time

def resume_pdf_embeddings(pdf_path: str, document_name: str = None):
    """Resume embedding a PDF from last checkpoint."""
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return False
    
    pdf_path = os.path.normpath(pdf_path)
    
    if document_name is None:
        document_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    try:
        load_dotenv()
        
        # Initialize managers
        processor = PDFProcessor()
        vector_store = VectorStore()
        checkpoint_manager = CheckpointManager()
        
        print(f"\n📄 Processing: {document_name}")
        print(f"📁 File: {pdf_path}")
        
        # Load checkpoint
        checkpoint = checkpoint_manager.load_checkpoint(document_name)
        print(f"\n✓ Checkpoint loaded:")
        print(f"  - Already processed: {checkpoint['processed_chunks']} chunks")
        print(f"  - Total to process: {checkpoint['total_chunks']}")
        
        # Process PDF
        print(f"\n🔄 Extracting and chunking PDF...")
        chunks = processor.process_pdf(pdf_path)
        print(f"✓ Created {len(chunks)} chunks total")
        
        # Get remaining chunks
        remaining_chunks = checkpoint_manager.get_remaining_chunks(chunks, checkpoint)
        print(f"✓ Found {len(remaining_chunks)} remaining chunks to process")
        
        if not remaining_chunks:
            print("\n✓ All chunks already processed!")
            stats = vector_store.get_stats()
            print(f"\nFinal Statistics:")
            print(f"  - Total documents in store: {stats['total_documents']}")
            return True
        
        # Process remaining chunks
        print(f"\n⏳ Starting embedding generation...")
        start_time = time.time()
        
        vector_store.add_documents_resumable(
            remaining_chunks,
            source="pdf",
            checkpoint_manager=checkpoint_manager,
            document_name=document_name
        )
        
        elapsed_time = time.time() - start_time
        
        # Get final statistics
        stats = vector_store.get_stats()
        final_checkpoint = checkpoint_manager.load_checkpoint(document_name)
        
        print(f"\n✅ Embedding process completed successfully!")
        print(f"\nResults:")
        print(f"  - Processed in this session: {len(remaining_chunks)} chunks")
        print(f"  - Total processed for {document_name}: {final_checkpoint['processed_chunks']} chunks")
        print(f"  - Time taken: {elapsed_time:.2f} seconds")
        print(f"  - Total documents in vector store: {stats['total_documents']}")
        
        # Show checkpoint status
        all_checkpoints = checkpoint_manager.list_all_checkpoints()
        if all_checkpoints:
            print(f"\nOther document checkpoints:")
            for doc, cp in all_checkpoints.items():
                if doc != document_name:
                    progress = cp['processed_chunks'] / max(cp['total_chunks'], 1) * 100
                    print(f"  - {doc}: {cp['processed_chunks']}/{cp['total_chunks']} ({progress:.1f}%)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during resumable embedding: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        document_name = sys.argv[2] if len(sys.argv) > 2 else None
        success = resume_pdf_embeddings(pdf_path, document_name)
    else:
        print("Usage: python scripts/resume_embeddings.py <pdf_path> [document_name]")
        print("Example: python scripts/resume_embeddings.py data/nephrology_reference.pdf nephrology")
        success = False
    
    sys.exit(0 if success else 1)
