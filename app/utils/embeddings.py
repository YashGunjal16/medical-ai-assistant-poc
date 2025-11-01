import google.generativeai as genai
from typing import List
import os
from app.utils.logger import logger

class EmbeddingsManager:
    """Manage embeddings using Google Generative AI."""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = "models/embedding-001"
        logger.info("EmbeddingsManager initialized with Gemini embedding model")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        embeddings = []
        for i, text in enumerate(texts):
            try:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
            except Exception as e:
                logger.error(f"Error on text {i}: {str(e)}")
                raise
        
        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_embeddings_batch_resumable(self, texts: List[str], 
                                       start_index: int = 0,
                                       callback=None) -> List[List[float]]:
        """
        Get embeddings for multiple texts with resumable capability.
        Added resumable embedding with progress tracking and error recovery
        """
        embeddings = []
        processed_count = start_index
        
        for i, text in enumerate(texts):
            try:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
                processed_count += 1
                
                # Call progress callback
                if callback and (i + 1) % 5 == 0:
                    callback(processed_count, start_index + len(texts))
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {processed_count}/{start_index + len(texts)} embeddings")
                    
            except Exception as e:
                logger.error(f"Error on text {i}: {str(e)}")
                # Continue processing instead of failing completely
                embeddings.append(None)
        
        logger.info(f"Successfully generated {len([e for e in embeddings if e])} embeddings")
        return embeddings
