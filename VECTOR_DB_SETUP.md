# Vector Database Setup Guide

## Overview
This Medical AI POC uses ChromaDB with Gemini embeddings for Retrieval-Augmented Generation (RAG). The system automatically processes PDFs and creates embeddings for medical document retrieval.

## Architecture

### Components
- **ChromaDB**: Vector database for storing and querying embeddings
- **Gemini API**: Free embedding model (`models/embedding-001`)
- **PDF Processor**: Extracts and chunks PDF text
- **Vector Store**: Manages embeddings and retrieval

### Flow
\`\`\`
PDF Upload → Chunk Text → Generate Embeddings (Gemini) → Store in ChromaDB → Retrieve on Query
\`\`\`

## Setup Instructions

### 1. Prerequisites
\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables in .env
GOOGLE_API_KEY=your_google_api_key
\`\`\`

### 2. Initialize Vector Store
\`\`\`bash
# Initialize with default reference materials
python scripts/init_vector_store.py
\`\`\`

This creates a ChromaDB collection with built-in nephrology reference materials.

### 3. Upload Your PDF
#### Option A: Using Streamlit UI
1. Run Streamlit: `streamlit run frontend/streamlit_app.py`
2. Go to sidebar → "Knowledge Base Management"
3. Upload your comprehensive nephrology PDF
4. Click "Process & Upload PDF"
5. Monitor the vector store stats

#### Option B: Using API
\`\`\`bash
curl -X POST http://localhost:8000/api/rag/upload-pdf \
  -F "file=@path/to/comprehensive-clinical-nephrology.pdf"
\`\`\`

#### Option C: Using Script
\`\`\`bash
python scripts/populate_vector_store.py --pdf-path path/to/file.pdf --source-name "nephrology_reference"
\`\`\`

### 4. Monitor Vector Store
\`\`\`bash
# Check vector store statistics
curl http://localhost:8000/api/rag/stats

# Expected response:
{
  "success": true,
  "stats": {
    "total_documents": 150,  # After PDF upload
    "collection_name": "medical_documents",
    "persist_dir": "app/vectorstore/chroma"
  }
}
\`\`\`

## Configuration

### PDF Processing Settings
Edit in `app/utils/pdf_processor.py`:
\`\`\`python
PDFProcessor(
    chunk_size=600,      # Characters per chunk
    chunk_overlap=150    # Overlap between chunks
)
\`\`\`

### Embedding Settings
Edit in `app/utils/embeddings.py`:
\`\`\`python
model = "models/embedding-001"  # Gemini embedding model
task_type="RETRIEVAL_DOCUMENT"  # Optimized for document retrieval
\`\`\`

### RAG Query Settings
Edit in `app/tools/rag_tool.py`:
\`\`\`python
n_results=3  # Number of chunks to retrieve per query
\`\`\`

## How It Works

### 1. PDF Ingestion
- PDFs are split into overlapping chunks (default: 600 chars, 150 overlap)
- Chunks are preserved with their original context
- Each chunk is assigned a unique ID

### 2. Embedding Generation
- Gemini's free embedding model generates 768-dimensional vectors
- Embeddings are created using `task_type="RETRIEVAL_DOCUMENT"`
- This is optimized for semantic search in medical documents

### 3. Storage
- Vectors are stored in ChromaDB with cosine distance metric
- Metadata (source, doc_id) is preserved for retrieval
- Data is persisted in `app/vectorstore/chroma/`

### 4. Retrieval
- Patient queries are embedded using the same model
- Semantic search finds most similar document chunks
- Results are ranked by cosine similarity
- Top N results are returned (default: 3)

## File Structure
\`\`\`
app/
├── vectorstore/
│   └── chroma/              # ChromaDB persistent storage
├── utils/
│   ├── pdf_processor.py     # PDF extraction and chunking
│   ├── embeddings.py        # Gemini embedding integration
│   └── vector_store.py      # ChromaDB management
├── tools/
│   └── rag_tool.py          # RAG query interface
└── main.py                  # API endpoint for PDF upload

scripts/
├── populate_vector_store.py # Batch PDF processing
└── init_vector_store.py     # Initialize vector store
\`\`\`

## API Endpoints

### Get Vector Store Stats
\`\`\`
GET /api/rag/stats

Response:
{
  "success": true,
  "stats": {
    "total_documents": 150,
    "collection_name": "medical_documents",
    "persist_dir": "app/vectorstore/chroma"
  }
}
\`\`\`

### Upload PDF
\`\`\`
POST /api/rag/upload-pdf
Content-Type: multipart/form-data

Response:
{
  "success": true,
  "message": "Successfully processed comprehensive-clinical-nephrology.pdf",
  "chunks_processed": 245,
  "total_documents": 395
}
\`\`\`

## Troubleshooting

### No embeddings generated
- Check `GOOGLE_API_KEY` is set correctly
- Verify API key has Generative Language API enabled
- Check rate limits (free tier has generous limits)

### PDF not chunking properly
- Verify PDF is text-based (not scanned images)
- Reduce chunk_size if getting incomplete chunks
- Check PDF encoding (UTF-8 preferred)

### Low retrieval quality
- Increase number of results: `n_results=5` or higher
- Adjust chunk overlap for better context
- Ensure PDF is relevant to queries
- Add more documents to improve coverage

### Performance issues
- Chunks process sequentially due to API rate limits
- Large PDFs may take a few minutes
- Queries are fast (cached embeddings)
- Use batch processing for multiple PDFs

## Cost
- **Gemini embeddings**: FREE (included in free tier)
- **ChromaDB**: Open source, runs locally
- **Storage**: Limited only by local disk space

## Next Steps
1. Upload your comprehensive nephrology PDF
2. Test queries about nephrology topics
3. Monitor retrieval quality in chat logs
4. Adjust chunking parameters if needed
5. Add more clinical documents as needed

## Reference
- ChromaDB: https://docs.trychroma.com/
- Google Generative AI: https://ai.google.dev/
- Embedding Models: https://ai.google.dev/models/embedding
\`\`\`

```bash file="" isHidden
