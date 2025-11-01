from fastapi import FastAPI, HTTPException, WebSocket, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
from datetime import datetime
from app.agents.receptionist_agent import ReceptionistAgent
from app.agents.clinical_agent import ClinicalAgent
from app.utils.logger import logger, log_interaction
from app.utils.pdf_processor import PDFProcessor
from app.tools.rag_tool import RAGManager
from dotenv import load_dotenv
import tempfile

load_dotenv()

app = FastAPI(
    title="Medical AI POC",
    description="Post-Discharge Patient Care AI Assistant",
    version="1.0.0"
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents and RAG
receptionist = ReceptionistAgent()
clinical_agent = ClinicalAgent()
rag_manager = RAGManager()

# Store active patient sessions
patient_sessions: Dict[str, Any] = {}


# ==================== Request Models ====================
class PatientGreetingRequest(BaseModel):
    patient_name: str


class PatientQueryRequest(BaseModel):
    patient_name: str
    session_id: str
    query: str


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str


# ==================== API Endpoints ====================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/greet")
async def greet_patient(request: PatientGreetingRequest):
    """
    Greet patient and retrieve their discharge report
    Initiates a new patient session
    """
    try:
        patient_name = request.patient_name.strip()
        
        if not patient_name:
            raise HTTPException(status_code=400, detail="Patient name is required")
        
        # Greet patient and retrieve data
        greeting_result = receptionist.greet_and_retrieve(patient_name)
        
        if not greeting_result["success"]:
            logger.warning(f"Patient greeting failed for: {patient_name}")
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": greeting_result["message"],
                    "patient_name": patient_name
                }
            )
        
        # Create patient session
        session_id = f"{patient_name.replace(' ', '_')}_{datetime.now().timestamp()}"
        patient_sessions[session_id] = {
            "patient_name": patient_name,
            "patient_data": greeting_result["patient_data"],
            "created_at": datetime.now().isoformat(),
            "interactions": []
        }
        
        logger.info(f"New session created for patient: {patient_name} (Session: {session_id})")
        
        return {
            "success": True,
            "message": greeting_result["message"],
            "session_id": session_id,
            "patient_data": {
                "name": greeting_result["patient_data"]["patient_name"],
                "diagnosis": greeting_result["patient_data"]["primary_diagnosis"],
                "age": greeting_result["patient_data"]["age"],
                "discharge_date": greeting_result["patient_data"]["discharge_date"]
            }
        }
    
    except Exception as e:
        logger.error(f"Error in greet_patient: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/chat")
async def handle_patient_chat(request: PatientQueryRequest):
    """
    Handle patient queries - routes to appropriate agent
    """
    try:
        session_id = request.session_id
        patient_name = request.patient_name
        patient_input = request.query.strip()
        
        if session_id not in patient_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not patient_input:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        session = patient_sessions[session_id]
        patient_data = session["patient_data"]
        
        # First pass: Check with receptionist for routing
        receptionist_response = receptionist.handle_patient_input(patient_name, patient_input, patient_data)
        
        if receptionist_response["route_to_clinical"]:
            # Route to clinical agent
            clinical_response = clinical_agent.handle_medical_query(
                patient_name,
                patient_input,
                patient_data
            )
            
            response_text = clinical_response["message"]
            agent_used = "Clinical Agent"
        else:
            # Use receptionist response
            response_text = receptionist_response["message"]
            agent_used = "Receptionist Agent"
        
        # Log interaction
        session["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_used,
            "user_input": patient_input,
            "response": response_text[:500]
        })
        
        logger.info(f"[{agent_used}] Processed query for {patient_name}")
        
        return {
            "success": True,
            "response": response_text,
            "agent_used": agent_used,
            "session_id": session_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in handle_patient_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Retrieve session information and chat history
    """
    try:
        if session_id not in patient_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = patient_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "patient_name": session["patient_name"],
            "created_at": session["created_at"],
            "interactions_count": len(session["interactions"]),
            "interactions": session["interactions"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_session_info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/patients")
async def get_all_patients():
    """
    Get list of all available patients for testing
    """
    try:
        from app.utils.helpers import get_all_patients
        patients = get_all_patients()
        
        return {
            "success": True,
            "total_patients": len(patients),
            "patients": patients
        }
    
    except Exception as e:
        logger.error(f"Error in get_all_patients: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/sessions/list")
async def list_sessions():
    """
    List all active sessions (for admin/testing)
    """
    try:
        sessions_info = []
        for session_id, session in patient_sessions.items():
            sessions_info.append({
                "session_id": session_id,
                "patient_name": session["patient_name"],
                "created_at": session["created_at"],
                "interaction_count": len(session["interactions"])
            })
        
        return {
            "success": True,
            "total_sessions": len(sessions_info),
            "sessions": sessions_info
        }
    
    except Exception as e:
        logger.error(f"Error in list_sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/logs")
async def get_system_logs():
    """
    Retrieve system logs (last 50 entries)
    """
    try:
        from pathlib import Path
        log_file = Path("logs/app.log")
        
        if not log_file.exists():
            return {
                "success": True,
                "logs": [],
                "message": "No logs available yet"
            }
        
        with open(log_file, "r") as f:
            logs = f.readlines()[-50:]  # Last 50 lines
        
        return {
            "success": True,
            "log_count": len(logs),
            "logs": logs
        }
    
    except Exception as e:
        logger.error(f"Error in get_system_logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/rag/stats")
async def get_rag_stats():
    """
    Get vector store statistics
    """
    try:
        stats = rag_manager.get_vector_store_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting RAG stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.post("/api/rag/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF file for RAG vector store
    """
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Process PDF
            pdf_processor = PDFProcessor(chunk_size=600, chunk_overlap=150)
            processed_chunks = pdf_processor.process_pdf(tmp_path)
            
            logger.info(f"Processed PDF: {file.filename} with {len(processed_chunks)} chunks")
            
            # Add to vector store
            result = rag_manager.add_pdf_documents(
                processed_chunks, 
                source=f"pdf_upload_{file.filename}"
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "message": f"Successfully processed {file.filename}",
                    "chunks_processed": len(processed_chunks),
                    "total_documents": result.get("total_documents", 0)
                }
            else:
                raise HTTPException(status_code=500, detail=result["message"])
        
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Medical AI POC Starting up...")
    logger.info("Initializing agents and RAG system...")
    stats = rag_manager.get_vector_store_stats()
    logger.info(f"Vector store ready with {stats.get('total_documents', 0)} documents")
    logger.info("System ready for patient interactions")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Medical AI POC Shutting down...")
    logger.info(f"Total sessions processed: {len(patient_sessions)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
