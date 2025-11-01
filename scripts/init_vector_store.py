"""
Script to initialize or sync vector store with PDF embeddings.
Useful for initial setup and periodic syncs.
Usage: python scripts/init_vector_store.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from app.utils.logger import logger
from app.tools.rag_tool import RAGManager
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    logger.info("Initializing vector store system...")
    
    try:
        # Initialize RAG manager (which initializes vector store with default materials)
        rag_manager = RAGManager()
        
        # Get statistics
        stats = rag_manager.get_vector_store_stats()
        
        logger.info("Vector store initialization complete!")
        logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
        
        print("\n✓ Vector store successfully initialized!")
        print(f"  - Total documents: {stats.get('total_documents', 0)}")
        print(f"  - Collection: {stats.get('collection_name', 'N/A')}")
        print(f"  - Storage: {stats.get('persist_dir', 'N/A')}")
        print("\nYou can now:")
        print("  1. Upload PDFs via the Streamlit UI")
        print("  2. Use the API endpoint: POST /api/rag/upload-pdf")
        print("  3. Queries will use embeddings from all documents")
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
