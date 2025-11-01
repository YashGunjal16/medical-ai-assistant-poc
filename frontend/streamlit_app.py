import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional
import tempfile
import os


# === START OF CHANGE ===
# Use an environment variable for the backend URL.
# This makes it work on Render and falls back to localhost for local testing.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") 
# === END OF CHANGE ===


# Set page config
st.set_page_config(
    page_title="Post-Discharge Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .medical-disclaimer {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .session-info {
        background-color: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .agent-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        font-weight: bold;
        margin-top: 0.5rem;
    }
    .receptionist {
        background-color: #d4edda;
        color: #155724;
    }
    .clinical {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

try:
    BACKEND_URL = st.secrets.get("backend_url", "http://localhost:8000")
except (FileNotFoundError, KeyError):
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "patient_name" not in st.session_state:
    st.session_state.patient_name = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "patient_data" not in st.session_state:
    st.session_state.patient_data = None


def greet_patient(patient_name: str):
    """Call backend to greet patient"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/greet",
            json={"patient_name": patient_name},
            timeout=30
        )
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Backend error: {response.status_code} - {response.text}"
            }
        
        data = response.json()
        if "success" not in data:
            return {
                "success": False,
                "message": "Invalid response format from backend",
                "raw_response": data
            }
        return data
    except requests.exceptions.JSONDecodeError:
        return {
            "success": False,
            "message": "Backend returned invalid JSON. Is the backend running?"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": f"Cannot connect to backend at {BACKEND_URL}. Make sure it's running."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def send_message(query: str):
    """Send message to backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "patient_name": st.session_state.patient_name,
                "session_id": st.session_state.session_id,
                "query": query
            },
            timeout=30
        )
        if response.status_code != 200:
            return {
                "success": False,
                "response": f"Error: {response.status_code} - {response.text}"
            }
        
        data = response.json()
        if "success" not in data:
            return {
                "success": False,
                "response": "Invalid response format from backend"
            }
        return data
    except requests.exceptions.JSONDecodeError:
        return {
            "success": False,
            "response": "Backend returned invalid JSON"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "response": f"Cannot connect to backend at {BACKEND_URL}"
        }
    except Exception as e:
        return {
            "success": False,
            "response": f"Error: {str(e)}"
        }


def get_all_patients():
    """Fetch list of available patients"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/patients",
            timeout=10
        )
        data = response.json()
        return data.get("patients", []) if data.get("success") else []
    except Exception as e:
        return []


def get_sessions_list():
    """Fetch active sessions"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/sessions/list",
            timeout=10
        )
        data = response.json()
        return data.get("sessions", []) if data.get("success") else []
    except Exception as e:
        return []


def upload_pdf_to_backend(file_bytes, filename: str):
    """Upload PDF file to backend RAG system"""
    try:
        files = {'file': (filename, file_bytes, 'application/pdf')}
        response = requests.post(
            f"{BACKEND_URL}/api/rag/upload-pdf",
            files=files,
            timeout=60  # Longer timeout for file processing
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Upload error: {str(e)}"}


def get_rag_stats():
    """Fetch RAG system statistics"""
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/rag/stats",
            timeout=10
        )
        data = response.json()
        return data.get("stats", {}) if data.get("success") else {}
    except Exception as e:
        return {}


# ==================== Debug & Connection Check ====================
def check_backend_connection():
    """Check if backend is reachable"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, "Connected"
        return False, f"Status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"Cannot reach {BACKEND_URL}"
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    # Check backend connection on app load
    is_connected, msg = check_backend_connection()
    if not is_connected:
        st.warning(f"⚠️ Backend not available: {msg}")
        st.info(f"Make sure FastAPI is running at {BACKEND_URL}")

# Main UI
st.title("🏥 Post-Discharge Medical AI Assistant")

# Medical disclaimer
st.markdown("""
<div class="medical-disclaimer">
    <strong>⚠️ Medical Disclaimer:</strong> This is an AI assistant for educational purposes only. 
    It is not a substitute for professional medical advice. Always consult with your healthcare provider 
    before making any medical decisions.
</div>
""", unsafe_allow_html=True)

# Sidebar for patient selection
with st.sidebar:
    st.header("Patient Portal")
    
    with st.expander("📚 Knowledge Base Management", expanded=False):
        st.subheader("Upload Medical Documents")
        st.write("Upload PDF files to enhance the AI's knowledge base with your clinical documents.")
        
        uploaded_file = st.file_uploader(
            "Choose PDF file",
            type="pdf",
            key="pdf_uploader"
        )
        
        if uploaded_file is not None:
            if st.button("Process & Upload PDF", key="upload_pdf_btn"):
                with st.spinner("Processing PDF and generating embeddings..."):
                    file_bytes = uploaded_file.read()
                    result = upload_pdf_to_backend(file_bytes, uploaded_file.name)
                    
                    if result.get("success"):
                        st.success(f"""
✓ PDF processed successfully!
- Chunks: {result.get('chunks_processed', 0)}
- Total documents in store: {result.get('total_documents', 0)}
                        """)
                    else:
                        st.error(f"Upload failed: {result.get('message', 'Unknown error')}")
        
        # Show vector store statistics
        st.divider()
        st.write("**Vector Store Statistics:**")
        stats = get_rag_stats()
        if stats:
            st.metric("Total Documents", stats.get("total_documents", 0))
            st.info(f"Collection: {stats.get('collection_name', 'N/A')}")
        else:
            st.warning("Could not fetch vector store stats")
    
    if st.session_state.session_id is None:
        st.subheader("Start New Session")
        
        # Option 1: Select from available patients
        st.write("**Select from available patients:**")
        patients = get_all_patients()
        
        if patients:
            selected_patient = st.selectbox(
                "Choose patient",
                patients,
                key="patient_selector"
            )
            
            if st.button("Load Patient", key="load_btn"):
                with st.spinner("Loading patient information..."):
                    result = greet_patient(selected_patient)
                    
                    if result["success"]:
                        st.session_state.session_id = result["session_id"]
                        st.session_state.patient_name = selected_patient
                        st.session_state.patient_data = result["patient_data"]
                        st.session_state.chat_history = []
                        st.rerun()
                    else:
                        st.error(result.get("message", "Failed to load patient"))
        else:
            st.warning("No patients available")
        
        # Option 2: Manual entry
        st.divider()
        st.write("**Or enter patient name manually:**")
        manual_patient = st.text_input("Patient Name")
        
        if st.button("Start Consultation", key="start_btn"):
            if manual_patient.strip():
                with st.spinner("Loading patient information..."):
                    result = greet_patient(manual_patient)
                    
                    if result["success"]:
                        st.session_state.session_id = result["session_id"]
                        st.session_state.patient_name = manual_patient
                        st.session_state.patient_data = result["patient_data"]
                        st.session_state.chat_history = []
                        st.rerun()
                    else:
                        st.error(result.get("message", "Patient not found"))
            else:
                st.warning("Please enter a patient name")
    
    else:
        # Show active session info
        st.markdown("""
<div class="session-info">
    <strong>📋 Active Session</strong>
</div>
        """, unsafe_allow_html=True)
        
        if st.session_state.patient_data:
            st.write(f"**Patient:** {st.session_state.patient_name}")
            st.write(f"**Age:** {st.session_state.patient_data.get('age', 'N/A')}")
            st.write(f"**Diagnosis:** {st.session_state.patient_data.get('diagnosis', 'N/A')}")
            st.write(f"**Discharge:** {st.session_state.patient_data.get('discharge_date', 'N/A')}")
        
        st.divider()
        
        if st.button("End Session", key="end_session"):
            st.session_state.session_id = None
            st.session_state.patient_name = None
            st.session_state.chat_history = []
            st.session_state.patient_data = None
            st.rerun()
    
    # Admin section
    with st.expander("📊 Admin & Debug"):
        st.subheader("Active Sessions")
        sessions = get_sessions_list()
        if sessions:
            for session in sessions:
                st.write(f"""
- **Patient:** {session['patient_name']}
- **Session ID:** {session['session_id'][:20]}...
- **Interactions:** {session['interaction_count']}
- **Created:** {session['created_at']}
                """)
        else:
            st.info("No active sessions")


# Main chat area
if st.session_state.session_id is not None:
    st.subheader(f"Chat with {st.session_state.patient_name}")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                if "agent" in message:
                    st.markdown(
                        f'<span class="agent-indicator {"clinical" if "Clinical" in message["agent"] else "receptionist"}">{message["agent"]}</span>',
                        unsafe_allow_html=True
                    )
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Send to backend
        with st.spinner("Processing..."):
            result = send_message(user_input)
        
        if result["success"]:
            # Add assistant response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["response"],
                "agent": result.get("agent_used", "Unknown Agent")
            })
            st.rerun()
        else:
            st.error(f"Error: {result.get('response', 'Unknown error')}")

else:
    st.info("👈 Select a patient from the sidebar to begin")
    
    # Welcome section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
### About This System
This AI-powered post-discharge care assistant helps patients:
- Review their discharge instructions
- Ask questions about their condition
- Receive medical guidance based on their diagnosis
- Maintain medication compliance
- Identify warning signs

### Key Features
- **Dual-Agent System**: Receptionist + Clinical AI
- **RAG Technology**: Uses medical reference materials
- **Patient Data**: Secure access to discharge reports
- **Web Search**: Latest medical research access
        """)
    
    with col2:
        st.markdown("""
### Getting Started
1. **Select a patient** from the sidebar
2. **Review** your discharge information
3. **Ask questions** about your care
4. **Receive guidance** from the Clinical AI

### Example Questions
- "What medications should I take?"
- "What are my warning signs?"
- "What restrictions do I need to follow?"
- "When should I contact my doctor?"
- "What is my condition about?"

### Note
Always consult your healthcare provider for serious concerns.
        """)
