"""
Script to populate ChromaDB with PDF embeddings.
Usage: python scripts/populate_vector_store.py --pdf-path path/to/file.pdf
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import json
from app.utils.pdf_processor import PDFProcessor
from app.utils.vector_store import VectorStore
from app.utils.logger import logger
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Populate vector store with PDF embeddings")
    parser.add_argument("--pdf-path", required=True, help="Path to PDF file")
    parser.add_argument("--source-name", default="nephrology_reference", help="Document source name")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        logger.error(f"PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    try:
        # Initialize components
        pdf_processor = PDFProcessor(chunk_size=600, chunk_overlap=150)
        vector_store = VectorStore()
        
        # Process PDF
        logger.info(f"Processing PDF: {args.pdf_path}")
        processed_chunks = pdf_processor.process_pdf(args.pdf_path)
        
        # Add to vector store
        logger.info(f"Adding {len(processed_chunks)} chunks to vector store...")
        vector_store.add_documents(processed_chunks, source=args.source_name)
        
        # Print stats
        stats = vector_store.get_stats()
        logger.info(f"Vector store stats: {json.dumps(stats, indent=2)}")
        
        print("\n✓ Successfully populated vector store!")
        print(f"  - Documents processed: {len(processed_chunks)}")
        print(f"  - Total documents in store: {stats['total_documents']}")
        
    except Exception as e:
        logger.error(f"Failed to populate vector store: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
