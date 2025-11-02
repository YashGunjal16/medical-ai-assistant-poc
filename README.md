# 🏥 Medical AI Assistant

> **AI-powered post-discharge patient care system using RAG, LangGraph, and Google Gemini**

An intelligent healthcare system designed to support patients after hospital discharge, particularly those with chronic kidney disease (CKD). The system uses multi-agent AI with RAG (Retrieval-Augmented Generation) to provide personalized, evidence-based medical guidance.

---

## 🎯 Key Features

- **🤖 Dual-Agent System**: Intelligent routing between receptionist and clinical agents
- **📚 RAG-Powered**: Semantic search through medical literature using ChromaDB
- **💾 Vector Database**: 768-dimensional Gemini embeddings for accurate retrieval
- **📄 PDF Knowledge Base**: Upload and query medical documents
- **🔍 Web Search Integration**: Fallback to Google Search and PubMed for latest research
- **🆓 Free to Run**: Uses Google Gemini's free API tier
- **⚕️ Safety-First**: Automatic medical disclaimers on all clinical responses

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Gemini API Key ([Get it free](https://makersuite.google.com/app/apikey))
- 4GB RAM minimum

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd medical-ai-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Initialize vector store
python scripts/init_vector_store.py

# 6. Start backend (Terminal 1)
uvicorn app.main:app --reload --port 8000

# 7. Start frontend (Terminal 2)
streamlit run frontend/streamlit_app.py
```

**Access the application:**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

### Docker Setup

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 2. Start services
docker-compose up -d

# 3. Initialize vector store
docker-compose exec backend python scripts/init_vector_store.py

# Access at http://localhost:8501
```

---

## 🏗️ Architecture

```
User Query
    ↓
Receptionist Agent (Routing)
    ├─→ Administrative → Direct Response
    └─→ Medical Query
          ↓
    Clinical Agent
          ├─→ RAG Retrieval (ChromaDB)
          ├─→ Web Search (if needed)
          └─→ Patient Context
          ↓
    Gemini 1.5 Flash
          ↓
    Response + Citations + Disclaimers
```

### Components

- **Receptionist Agent**: Patient greeting, session management, query routing
- **Clinical Agent**: Medical query processing with RAG and web search
- **RAG System**: PDF processing, embeddings, semantic search
- **Vector Store**: ChromaDB with persistent storage
- **Patient Database**: 45+ dummy discharge reports for testing

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | Async REST API |
| **Frontend** | Streamlit | Chat interface |
| **LLM** | Google Gemini 2.5 Flash | Text generation |
| **Embeddings** | Gemini Embeddings | 768-dim vectors |
| **Vector DB** | ChromaDB | Semantic search |
| **Agents** | LangGraph | Multi-agent orchestration |
| **PDF Processing** | PyPDF2 | Document extraction |

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
LOG_LEVEL=INFO
```

### Chunking Settings

Edit `app/utils/pdf_processor.py`:

```python
CHUNK_SIZE = 700        # Characters per chunk
CHUNK_OVERLAP = 150     # Overlap for context
```

---

## 📁 Project Structure

```
medical-ai-assistant/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── __init__.py
│   ├── agents/
│   │   ├── clinical_agent.py      # Medical queries
│   │   └── receptionist_agent.py  # Patient greeting & routing
│   ├── data/
│   │   ├── patients.json          # 25 dummy patients
│   │   └── nephrology_reference.pdf
│   ├── tools/
│   │   ├── db_tool.py             # Patient database
│   │   ├── rag_tool.py            # RAG interface
│   │   └── web_search_tool.py     # Google/PubMed search
│   ├── utils/
│   │   ├── checkpoint_manager.py  # Embedding progress tracking
│   │   ├── embeddings.py          # Gemini embeddings
│   │   ├── helpers.py             # Utility functions
│   │   ├── logger.py              # Logging system
│   │   ├── model_config.py        # LLM configuration
│   │   ├── pdf_processor.py       # PDF chunking
│   │   └── vector_store.py        # ChromaDB ops
│   └── vectorstore/
│       ├── chroma/                # Persistent vector DB
│       └── checkpoints/           # Embedding checkpoints
├── frontend/
│   └── streamlit_app.py           # UI
├── logs/
│   ├── agent_handoffs.jsonl       # Agent routing logs
│   ├── app.log                    # Application logs
│   ├── interactions.jsonl         # Chat history
│   └── retrievals.jsonl           # RAG retrieval logs
├── processing docs pro/           # Documentation
│   ├── ARCHITECTURE_REPORT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── PROJECT_VERIFICATION_CHECKLIST.md
│   ├── VECTOR_DB_SETUP.md
│   └── WORKFLOW_EXAMPLES.md
├── scripts/
│   ├── demo_workflow.py           # Demo script
│   ├── embedding_status.py        # Check embedding progress
│   ├── init_vector_store.py       # Initialize DB
│   ├── list_available_models.py   # List Gemini models
│   ├── populate_vector_store.py   # Batch PDF upload
│   ├── resume_embeddings.py       # Resume interrupted embeddings
│   └── sync_existing_embeddings.py # Checkpoint sync
├── testing/                       # Test files
├── .env                           # Environment config (not in git)
├── .env.example                   # Environment template
├── .gitattributes
├── .gitignore
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Container definition
├── package.json                   # Node dependencies (if any)
├── README.md                      # This file
├── render.yaml                    # Render.com deployment
├── requirements.txt               # Python dependencies
└── start.sh                       # Startup script
```

---

## 🔧 Troubleshooting

### Common Issues

**"GOOGLE_API_KEY not set"**
```bash
cp .env.example .env
# Add your API key to .env
```

**"No embeddings found"**
```bash
python scripts/init_vector_store.py
```

**"Batch size exceeds maximum"**
```python
# Edit app/utils/vector_store.py
batch_size=5000  # Reduce from 10000
```

**Slow responses**
- Check internet connection (for web search)
- Reduce chunk size in PDF processor
- Monitor Gemini API rate limits

---

## 📊 Performance

| Metric | Average |
|--------|---------|
| Patient Greeting | 5-10s |
| Medical Query (RAG) | 15-25s |
| PDF Upload (100 pages) | 2-3 min |
| Semantic Search | <100ms |

**Tested Capacity:**
- 15,000+ documents in vector store
- 10-20 concurrent users (single instance)
- 500MB-1GB memory usage

---

## ⚠️ Medical Disclaimer

**IMPORTANT**: This is an educational AI system for demonstration purposes only.

- ❌ NOT a substitute for professional medical advice
- ❌ NOT for clinical decision-making
- ✅ Always consult qualified healthcare professionals
- ✅ For emergencies, call 911 or local emergency services

---

## 🚀 Future Enhancements

- [ ] Deploy to Render.com
- [ ] Multi-language support
- [ ] Enhanced medical embeddings (BioBERT)
- [ ] Medication interaction checker
- [ ] HIPAA compliance features
- [ ] Mobile app

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Yash Gunjal**  
Developer and Maintainer of *Medical AI Assistant POC*

- [GitHub](https://github.com/YashGunjal16)
- [LinkedIn](www.linkedin.com/in/yash-gunjal-5b728125b)
- 📧 yash830gunjal@gmail.com

---

## 🙏 Acknowledgments

- **Google Gemini Team** - Free LLM API
- **ChromaDB Team** - Vector database
- **LangChain Team** - Agent framework
- **Medical Resources** - KDIGO, ADA, NKF guidelines

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/medical-ai-assistant/issues)
- **Documentation**: See README and inline comments
- **API Docs**: http://localhost:8000/docs

---

**Built with ❤️ for better healthcare outcomes**

*⭐ Star this repository if you find it useful!*
