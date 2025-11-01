import PyPDF2
import os
import hashlib
from typing import List, Tuple
from app.utils.logger import logger

class PDFProcessor:
    """Extract and chunk PDF text for embeddings."""
    
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            pdf_path = os.path.normpath(pdf_path)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"Processing PDF with {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > self.chunk_size // 2:
                    end = start + last_period + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[Tuple[str, str]]:
        """Extract, chunk, and return processed PDF content."""
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Create deterministic ID based on chunk content and position
            chunk_hash = hashlib.md5(f"{i}_{chunk[:100]}".encode()).hexdigest()[:8]
            chunk_id = f"chunk_{i:06d}_{chunk_hash}"
            processed_chunks.append((chunk_id, chunk))
        
        return processed_chunks

