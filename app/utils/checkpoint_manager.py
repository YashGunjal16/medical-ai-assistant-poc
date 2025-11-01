import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
from app.utils.logger import logger

class CheckpointManager:
    """Manage embedding progress checkpoints for resumable processing."""
    
    def __init__(self, checkpoint_dir: str = "app/vectorstore/checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
        logger.info(f"CheckpointManager initialized at {checkpoint_dir}")
    
    def get_checkpoint_file(self, document_name: str) -> str:
        """Get checkpoint file path for a document."""
        return os.path.join(self.checkpoint_dir, f"{document_name}_checkpoint.json")
    
    def save_checkpoint(self, document_name: str, progress: Dict) -> None:
        """Save progress checkpoint for a document."""
        try:
            checkpoint_file = self.get_checkpoint_file(document_name)
            progress['last_updated'] = datetime.now().isoformat()
            progress['document_name'] = document_name
            
            with open(checkpoint_file, 'w') as f:
                json.dump(progress, f, indent=2)
            
            logger.info(f"Checkpoint saved for {document_name}: {progress}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {str(e)}")
            raise
    
    def load_checkpoint(self, document_name: str) -> Dict:
        """Load progress checkpoint for a document."""
        try:
            checkpoint_file = self.get_checkpoint_file(document_name)
            
            if not os.path.exists(checkpoint_file):
                logger.info(f"No checkpoint found for {document_name}, starting fresh")
                return {
                    "processed_chunks": 0,
                    "total_chunks": 0,
                    "processed_ids": [],
                    "document_name": document_name
                }
            
            with open(checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            
            logger.info(f"Loaded checkpoint for {document_name}: {checkpoint['processed_chunks']}/{checkpoint['total_chunks']}")
            return checkpoint
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")
            return {
                "processed_chunks": 0,
                "total_chunks": 0,
                "processed_ids": [],
                "document_name": document_name
            }
    
    def get_remaining_chunks(self, all_chunks: List[Tuple[str, str]], 
                             checkpoint: Dict) -> List[Tuple[str, str]]:
        """Filter out already processed chunks."""
        processed_ids = set(checkpoint.get('processed_ids', []))
        remaining = [chunk for chunk in all_chunks if chunk[0] not in processed_ids]
        
        logger.info(f"Resuming from {checkpoint['processed_chunks']}: {len(remaining)} chunks remaining")
        return remaining
    
    def list_all_checkpoints(self) -> Dict[str, Dict]:
        """List all saved checkpoints."""
        checkpoints = {}
        
        if os.path.exists(self.checkpoint_dir):
            for file in os.listdir(self.checkpoint_dir):
                if file.endswith('_checkpoint.json'):
                    doc_name = file.replace('_checkpoint.json', '')
                    checkpoint = self.load_checkpoint(doc_name)
                    checkpoints[doc_name] = checkpoint
        
        return checkpoints
    
    def reset_checkpoint(self, document_name: str) -> None:
        """Reset checkpoint for a document to start fresh."""
        try:
            checkpoint_file = self.get_checkpoint_file(document_name)
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)
                logger.info(f"Checkpoint reset for {document_name}")
        except Exception as e:
            logger.error(f"Error resetting checkpoint: {str(e)}")
            raise
