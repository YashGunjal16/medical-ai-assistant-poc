# Medical AI POC - Post-Discharge Care Assistant

A production-ready Proof of Concept for an AI-powered post-discharge patient care system using FastAPI, LangGraph, Streamlit, and ChromaDB with Google Gemini.

## Overview

This system implements a dual-agent architecture for managing post-discharge patient care:
- **Receptionist Agent**: Greets patients and retrieves discharge reports
- **Clinical Agent**: Handles medical queries using RAG and provides evidence-based guidance
- **RAG System**: Leverages ChromaDB with Gemini embeddings for semantic document retrieval
- **Vector Database**: Supports PDF uploads with automatic chunking and embedding generation

## Features

✅ **Multi-Agent Architecture** - LangGraph-based orchestration
✅ **RAG Implementation** - ChromaDB with Gemini embeddings (free tier)
✅ **PDF Management** - Upload, chunk, and embed medical documents
✅ **Vector Database** - Full-text semantic search with free Gemini embeddings
✅ **Patient Database** - 25+ dummy discharge reports
✅ **Web Search Integration** - Fallback for latest information
✅ **Comprehensive Logging** - All interactions tracked
✅ **FastAPI Backend** - RESTful endpoints with PDF upload
✅ **Streamlit UI** - Interactive patient interface with knowledge base management
✅ **Docker Support** - Ready for deployment
✅ **Render.com Ready** - Direct deployment configuration

## Project Structure

\`\`\`
medical_ai_poc/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── receptionist_agent.py
│   │   └── clinical_agent.py
│   ├── tools/
│   │   ├── rag_tool.py
│   │   ├── db_tool.py
│   │   └── web_search_tool.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── helpers.py
│   │   ├── pdf_processor.py       # NEW: PDF extraction and chunking
│   │   ├── embeddings.py          # NEW: Gemini embeddings integration
│   │   └── vector_store.py        # NEW: ChromaDB vector store management
│   ├── data/
│   │   └── patients.json
│   └── vectorstore/
│       └── chroma/                # NEW: Persistent vector database
├── frontend/
│   └── streamlit_app.py
├── scripts/
│   ├── populate_vector_store.py   # NEW: Batch PDF processing
│   └── init_vector_store.py       # NEW: Vector store initialization
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── render.yaml
├── VECTOR_DB_SETUP.md             # NEW: Vector DB documentation
└── README.md
\`\`\`

## Quick Start

### Option 1: Local Development (Fastest)

\`\`\`bash
# Clone and setup
git clone <repository-url>
cd medical_ai_poc
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Initialize vector store with default materials
python scripts/init_vector_store.py

# Terminal 1: Run backend
uvicorn app.main:app --reload
# http://localhost:8000

# Terminal 2: Run frontend
streamlit run frontend/streamlit_app.py
# http://localhost:8501
\`\`\`

### Option 2: Docker (Recommended)

\`\`\`bash
# Clone and setup
git clone <repository-url>
cd medical_ai_poc

# Create .env file
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Build and run
docker-compose up -d

# Access
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
# Chroma DB: http://localhost:8000
\`\`\`

### Option 3: Render.com Deployment

1. Push code to GitHub
2. Connect to Render.com
3. Create services using `render.yaml`
4. Set `GOOGLE_API_KEY` environment variable
5. Deploy automatically on push

## Vector Database Setup

### Initialize Vector Store

\`\`\`bash
# Initialize with default nephrology reference materials
python scripts/init_vector_store.py

# This creates:
# - ChromaDB collection with Gemini embeddings
# - 5 reference material categories
# - ~100+ initial document chunks
\`\`\`

### Upload Medical PDFs

#### Via Streamlit UI
1. Open Streamlit frontend: http://localhost:8501
2. Sidebar → "Knowledge Base Management" (expanded)
3. Upload PDF file
4. Click "Process & Upload PDF"
5. Monitor vector store stats

#### Via API
\`\`\`bash
curl -X POST http://localhost:8000/api/rag/upload-pdf \
  -F "file=@/path/to/comprehensive-clinical-nephrology.pdf"
\`\`\`

#### Via Script
\`\`\`bash
python scripts/populate_vector_store.py \
  --pdf-path /path/to/file.pdf \
  --source-name "nephrology_reference"
\`\`\`

### Check Vector Store Status
\`\`\`bash
curl http://localhost:8000/api/rag/stats

# Response:
{
  "success": true,
  "stats": {
    "total_documents": 250,
    "collection_name": "medical_documents",
    "persist_dir": "app/vectorstore/chroma"
  }
}
\`\`\`

## API Endpoints

### Core Patient Endpoints

**Health Check**
\`\`\`bash
GET /health
\`\`\`

**Greet Patient & Start Session**
\`\`\`bash
POST /api/greet
Content-Type: application/json

{"patient_name": "John Smith"}
\`\`\`

**Send Message to Patient**
\`\`\`bash
POST /api/chat
Content-Type: application/json

{
  "patient_name": "John Smith",
  "session_id": "unique_session_id",
  "query": "What should I eat?"
}
\`\`\`

**Get Session Information**
\`\`\`bash
GET /api/session/{session_id}
\`\`\`

### Admin Endpoints

**List All Patients**
\`\`\`bash
GET /api/patients
\`\`\`

**List Active Sessions**
\`\`\`bash
POST /api/sessions/list
\`\`\`

**Get System Logs**
\`\`\`bash
GET /api/logs
\`\`\`

### Vector Database Endpoints

**Get Vector Store Stats**
\`\`\`bash
GET /api/rag/stats
\`\`\`

**Upload PDF to Vector Store**
\`\`\`bash
POST /api/rag/upload-pdf
Content-Type: multipart/form-data

file: <PDF file>
\`\`\`

## Embedding Details

### Gemini Embedding Model
- **Model**: `models/embedding-001`
- **Embedding Dimension**: 768
- **Cost**: FREE (included in free tier)
- **Task Type**: RETRIEVAL_DOCUMENT (optimized for semantic search)

### Chunking Strategy
- **Chunk Size**: 600 characters
- **Overlap**: 150 characters
- **Strategy**: Recursive text splitting with sentence boundaries
- **Purpose**: Balance context preservation with retrieval precision

### Retrieval Strategy
- **Algorithm**: Cosine similarity search
- **Default Results**: Top 3 most similar chunks
- **Distance Metric**: Cosine distance (lower = more similar)
- **Augmentation**: Retrieved chunks injected into LLM prompt

## Usage Examples

### Python Client Example
\`\`\`python
import requests

BASE_URL = "http://localhost:8000"

# 1. Greet patient
response = requests.post(
    f"{BASE_URL}/api/greet",
    json={"patient_name": "John Smith"}
)
data = response.json()
session_id = data["session_id"]
print(f"Greeting: {data['message']}")

# 2. Send message
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "patient_name": "John Smith",
        "session_id": session_id,
        "query": "What are my warning signs?"
    }
)
data = response.json()
print(f"Agent Used: {data['agent_used']}")
print(f"Response: {data['response']}")

# 3. Upload PDF
with open("nephrology.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/api/rag/upload-pdf",
        files={"file": f}
    )
    print(response.json())

# 4. Check vector store
response = requests.get(f"{BASE_URL}/api/rag/stats")
print(response.json()["stats"])
\`\`\`

## Logging

All interactions logged to `logs/` directory:
- **app.log** - General application logs
- **interactions.jsonl** - Patient chat interactions
- **agent_handoffs.jsonl** - Receptionist to clinical routing decisions
- **retrievals.jsonl** - RAG retrieval attempts with results

Example log:
\`\`\`json
{
  "timestamp": "2024-01-20T10:30:45.123456",
  "patient_name": "John Smith",
  "agent": "Clinical Agent",
  "query": "What medications should I take?",
  "retrieved_chunks": 3,
  "retrieval_successful": true
}
\`\`\`

## Deployment

### On Render.com

1. **Push to GitHub**
   \`\`\`bash
   git push origin main
   \`\`\`

2. **Create Render Services**
   - Go to https://dashboard.render.com
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repository
   - Render will detect render.yaml and auto-configure

3. **Set Environment Variables**
   - Dashboard → Environment
   - Add: `GOOGLE_API_KEY=your_key`
   - Add: `GOOGLE_SEARCH_API_KEY=your_key` (optional)

4. **Auto Deploy**
   - Any push to main triggers deployment
   - Services run on free tier (with cold starts)

### On Other Platforms

The system works on any platform supporting Docker:
- AWS ECS
- Google Cloud Run
- DigitalOcean App Platform
- Heroku (with procfile)

## Performance

- **Embedding Generation**: ~0.5-1 second per chunk (Gemini API)
- **Semantic Search**: <100ms (in-memory ChromaDB)
- **RAG Query**: 2-5 seconds total (embedding + search + LLM)
- **PDF Processing**: ~1-2 minutes per 100-page document
- **Storage**: ~500KB per 1000 document chunks

## Troubleshooting

### Vector Store Issues
- **No documents found**: Run `python scripts/init_vector_store.py`
- **Upload fails**: Check file is PDF and <50MB
- **Slow retrieval**: Increase `n_results` parameter in RAG tool

### PDF Processing Issues
- **Encoding errors**: Ensure PDF is text-based (not scanned images)
- **Large files**: Process in batches using the script
- **API timeouts**: Check Gemini API rate limits

### Deployment Issues
- **CORS errors**: Already configured in FastAPI
- **Port conflicts**: Change ports in docker-compose.yml
- **Memory issues**: Reduce chunk size or use cloud deployment

## Future Enhancements

- [ ] Multi-language support with translation
- [ ] Advanced analytics dashboard
- [ ] Real-time notifications and reminders
- [ ] Video consultation integration
- [ ] EHR system integration
- [ ] Advanced search with filters
- [ ] Document versioning and updates
- [ ] Specialized embeddings for medical terminology

## Technologies

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Streamlit
- **LLM**: Google Gemini (free tier)
- **Embeddings**: Gemini embeddings (free)
- **Vector DB**: ChromaDB (open source)
- **Agents**: LangGraph
- **PDF Processing**: PyPDF2
- **Deployment**: Docker, Render.com

## Security Notes

- All data is processed locally (ChromaDB)
- Embeddings sent to Gemini API only
- No data stored on Render.com (ephemeral)
- Use `.env` for sensitive variables
- Never commit `.env` to git

## Support & Documentation

- See `VECTOR_DB_SETUP.md` for detailed vector database configuration
- Check `logs/` directory for debugging
- Review API documentation at http://localhost:8000/docs

---

**Medical AI for Better Patient Outcomes**
