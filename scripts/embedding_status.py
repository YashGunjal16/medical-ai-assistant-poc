"""
Check status of all embedding checkpoints and show progress.
Usage: python scripts/embedding_status.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.checkpoint_manager import CheckpointManager
from app.utils.vector_store import VectorStore
from app.utils.logger import logger
from dotenv import load_dotenv
from datetime import datetime

def show_embedding_status():
    """Display status of all embedding processes."""
    
    try:
        load_dotenv()
        
        checkpoint_manager = CheckpointManager()
        vector_store = VectorStore()
        
        print("\n" + "="*70)
        print("📊 EMBEDDING STATUS DASHBOARD")
        print("="*70)
        
        # Get all checkpoints
        checkpoints = checkpoint_manager.list_all_checkpoints()
        
        if not checkpoints:
            print("\n✓ No active checkpoints found. Vector store is ready for new documents.")
        else:
            print(f"\nFound {len(checkpoints)} document(s) in progress:\n")
            
            total_processed = 0
            total_remaining = 0
            
            for doc_name, checkpoint in checkpoints.items():
                processed = checkpoint['processed_chunks']
                total = checkpoint['total_chunks']
                remaining = total - processed
                progress_pct = (processed / max(total, 1)) * 100
                
                total_processed += processed
                total_remaining += remaining
                
                # Progress bar
                bar_length = 40
                filled = int(bar_length * progress_pct / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                
                print(f"📄 {doc_name}")
                print(f"   [{bar}] {progress_pct:.1f}%")
                print(f"   Processed: {processed}/{total} chunks")
                print(f"   Remaining: {remaining} chunks")
                
                if 'last_updated' in checkpoint:
                    last_update = datetime.fromisoformat(checkpoint['last_updated'])
                    print(f"   Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        
        # Vector store stats
        stats = vector_store.get_stats()
        print("\n" + "-"*70)
        print("📦 VECTOR STORE STATISTICS")
        print("-"*70)
        print(f"Total documents in store: {stats['total_documents']}")
        print(f"Collection name: {stats['collection_name']}")
        print(f"Storage location: {stats['persist_dir']}")
        
        if checkpoints:
            print(f"\nOverall Progress: {total_processed}/{total_processed + total_remaining} chunks")
            if total_processed + total_remaining > 0:
                overall_pct = (total_processed / (total_processed + total_remaining)) * 100
                print(f"Overall completion: {overall_pct:.1f}%")
        
        print("\n" + "="*70)
        print("✓ Use 'python scripts/resume_embeddings.py <pdf_path>' to continue processing")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Error showing embedding status: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    show_embedding_status()
