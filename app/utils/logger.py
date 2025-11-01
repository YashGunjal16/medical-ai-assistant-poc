import logging
import json
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_interaction(patient_name: str, agent: str, message: str, response: str, interaction_type: str = "chat"):
    """Log patient interactions with agents"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "patient_name": patient_name,
        "agent": agent,
        "interaction_type": interaction_type,
        "message": message,
        "response": response[:500],  # Limit response length in logs
    }
    
    with open(logs_dir / "interactions.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    logger.info(f"[{agent}] Interaction with {patient_name}: {interaction_type}")


def log_agent_handoff(from_agent: str, to_agent: str, reason: str, patient_name: str):
    """Log agent handoff events"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "reason": reason,
        "patient_name": patient_name,
    }
    
    with open(logs_dir / "agent_handoffs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    logger.info(f"Handoff from {from_agent} to {to_agent} for patient {patient_name}: {reason}")


def log_retrieval_attempt(retrieval_type: str, query: str, success: bool, source: str = "unknown"):
    """Log database and vector store retrieval attempts"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "retrieval_type": retrieval_type,
        "query": query,
        "success": success,
        "source": source,
    }
    
    with open(logs_dir / "retrievals.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    logger.info(f"Retrieval [{retrieval_type}] from {source}: {query} - Success: {success}")
