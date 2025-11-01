import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Tuple
from app.utils.logger import logger
from app.utils.embeddings import EmbeddingsManager
import json

class VectorStore:
    """Manage ChromaDB vector store operations."""
    
    def __init__(self, persist_dir: str = None):
         # === START OF CHANGE ===
        # Use an environment variable for the persist directory, with a local default.
        # This is the key change for Render compatibility.
        self.persist_dir = persist_dir or os.getenv("VECTOR_STORE_PATH", "vectorstore/chroma")
        # === END OF CHANGE ===
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embeddings_manager = EmbeddingsManager()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="medical_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"VectorStore initialized with collection: medical_documents")
    
    def add_documents(self, documents: List[Tuple[str, str]], source: str = "pdf"):
        """Add documents to vector store with embeddings."""
        try:
            chunk_ids = []
            chunk_texts = []
            metadatas = []
            
            for doc_id, text in documents:
                chunk_ids.append(doc_id)
                chunk_texts.append(text)
                metadatas.append({
                    "source": source,
                    "doc_id": doc_id
                })
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunk_texts)} documents...")
            embeddings = self.embeddings_manager.get_embeddings_batch(chunk_texts)
            
            # Add to collection
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def add_documents_resumable(self, documents: List[Tuple[str, str]], 
                                source: str = "pdf",
                                checkpoint_manager = None,
                                document_name: str = "default",
                                batch_size: int = 5000):  # ADD THIS PARAMETER
        """
        Add documents to vector store with resumable capability.
        Added resumable document addition with checkpoint support for resuming interrupted processing
        """
        try:
            # Load checkpoint if available
            checkpoint = None
            remaining_docs = documents
            processed_count = 0
            
            if checkpoint_manager:
                checkpoint = checkpoint_manager.load_checkpoint(document_name)
                remaining_docs = checkpoint_manager.get_remaining_chunks(documents, checkpoint)
                processed_count = checkpoint.get('processed_chunks', 0)
            
            chunk_ids = []
            chunk_texts = []
            metadatas = []
            newly_processed_ids = checkpoint.get('processed_ids', []) if checkpoint else []
            
            for doc_id, text in remaining_docs:
                chunk_ids.append(doc_id)
                chunk_texts.append(text)
                metadatas.append({
                    "source": source,
                    "doc_id": doc_id
                })
            
            if not chunk_ids:
                logger.info("All documents already processed, skipping")
                return True
            
            # Generate embeddings with resumable support
            logger.info(f"Generating embeddings for {len(chunk_texts)} documents...")
            
            def progress_callback(current, total):
                logger.info(f"Progress: {current}/{total} embeddings generated")
            
            embeddings = self.embeddings_manager.get_embeddings_batch_resumable(
                chunk_texts, 
                start_index=processed_count,
                callback=progress_callback
            )
            
            # Filter out None embeddings (errors)
            valid_embeddings = []
            valid_ids = []
            valid_texts = []
            valid_metadatas = []
            
            for emb, doc_id, text, meta in zip(embeddings, chunk_ids, chunk_texts, metadatas):
                if emb is not None:
                    valid_embeddings.append(emb)
                    valid_ids.append(doc_id)
                    valid_texts.append(text)
                    valid_metadatas.append(meta)
                    newly_processed_ids.append(doc_id)
            
            # === FIX: ADD TO COLLECTION IN BATCHES ===
            if valid_ids:
                logger.info(f"Adding {len(valid_ids)} documents in batches of {batch_size}...")
                
                # Process in batches to avoid ChromaDB batch size limit
                for i in range(0, len(valid_ids), batch_size):
                    batch_end = min(i + batch_size, len(valid_ids))
                    
                    self.collection.add(
                        ids=valid_ids[i:batch_end],
                        embeddings=valid_embeddings[i:batch_end],
                        documents=valid_texts[i:batch_end],
                        metadatas=valid_metadatas[i:batch_end]
                    )
                    
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(valid_ids) + batch_size - 1) // batch_size
                    logger.info(f"Added batch {batch_num}/{total_batches}: {batch_end}/{len(valid_ids)} documents")
                
                logger.info(f"Successfully added all {len(valid_ids)} documents to vector store")
            
            # Save checkpoint
            if checkpoint_manager:
                updated_checkpoint = {
                    "processed_chunks": processed_count + len(valid_ids),
                    "total_chunks": len(documents),
                    "processed_ids": newly_processed_ids,
                    "document_name": document_name
                }
                checkpoint_manager.save_checkpoint(document_name, updated_checkpoint)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for similar documents."""
        try:
            # Generate embedding for query
            query_embedding = self.embeddings_manager.get_embedding(query)
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            logger.info(f"Search query retrieved {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "medical_documents",
                "persist_dir": self.persist_dir
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            raise
