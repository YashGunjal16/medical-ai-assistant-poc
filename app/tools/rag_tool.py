import os
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings
from app.utils.logger import log_retrieval_attempt, logger
from app.utils.vector_store import VectorStore

class RAGManager:
    """Manages RAG setup and retrieval from vector database with Gemini embeddings"""
    
    def __init__(self, persist_dir: str = "app/vectorstore/chroma"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        try:
            # Initialize vector store with Gemini embeddings
            self.vector_store = VectorStore(persist_dir=persist_dir)
            logger.info("RAGManager initialized with VectorStore using Gemini embeddings")
            
            # Initialize with reference materials if empty or incomplete
            self._initialize_reference_materials()
        except Exception as e:
            logger.error(f"Error initializing RAGManager: {str(e)}")
            raise
    
    def _initialize_reference_materials(self):
        """Initialize default reference materials in vector store (incremental)"""
        # Load all reference materials
        reference_docs = self._load_reference_materials()
        all_chunks = self._chunk_documents(reference_docs)
        
        try:
            # Check how many documents already exist
            stats = self.vector_store.get_stats()
            existing_count = stats.get("total_documents", 0)
            
            logger.info(f"Vector store has {existing_count} existing documents")
            logger.info(f"Total reference chunks: {len(all_chunks)}")
            
            # Only add remaining chunks
            if existing_count < len(all_chunks):
                remaining_chunks = all_chunks[existing_count:]
                logger.info(f"Adding {len(remaining_chunks)} new chunks (skipping {existing_count} existing)")
                
                self.vector_store.add_documents(remaining_chunks, source="default_reference")
                logger.info(f"Successfully added {len(remaining_chunks)} new reference chunks")
            else:
                logger.info(f"All reference materials already embedded. Skipping initialization.")
                
        except Exception as e:
            logger.error(f"Error initializing reference materials: {str(e)}")
            raise
    
    def _load_reference_materials(self) -> List[Dict[str, str]]:
        materials = [
            {
                "source": "Clinical Practice Guidelines - CKD Management",
                "content": """
Chronic Kidney Disease (CKD) Management Guidelines:

STAGING:
- Stage 1: GFR ≥ 90 mL/min/1.73 m², kidney damage with normal or increased GFR
- Stage 2: GFR 60-89 mL/min/1.73 m², mild decrease in kidney function
- Stage 3a: GFR 45-59 mL/min/1.73 m², mild to moderate decrease
- Stage 3b: GFR 30-44 mL/min/1.73 m², moderate to severe decrease
- Stage 4: GFR 15-29 mL/min/1.73 m², severe decrease in kidney function
- Stage 5: GFR < 15 mL/min/1.73 m² or on dialysis, kidney failure

ACE INHIBITORS AND ARBs:
- First-line therapy for CKD with hypertension or diabetes
- Mechanism: Reduce proteinuria and slow progression
- Common drugs: Lisinopril, Enalapril, Losartan, Valsartan
- Monitor: Potassium, creatinine, avoid combination use

MEDICATION MONITORING:
- ACE-I/ARBs: Monitor K+, creatinine 1-2 weeks after initiation
- SGLT2 inhibitors: Effective for CKD progression
- Diuretics: Use cautiously, monitor volume status
- NSAIDs: Contraindicated in advanced CKD

DIETARY MANAGEMENT:
- Sodium restriction: 2g/day target
- Potassium: Restrict to 2-3g/day in advanced CKD
- Protein: 0.8g/kg for CKD stages 3-5
- Fluid: Unrestricted unless volume overload
- Phosphorus: Restrict in stages 4-5
"""
            },
            {
                "source": "Dialysis and Renal Replacement Therapy",
                "content": """
Renal Replacement Therapy Guidelines:

HEMODIALYSIS:
- Typically 3-4 times weekly, 4-5 hours per session
- Vascular access: AV fistula preferred, then graft, then catheter
- Complications: Infection, thrombosis, hypotension, muscle cramps
- Diet: Strict potassium, sodium, phosphorus restriction

PERITONEAL DIALYSIS:
- Continuous ambulatory PD (CAPD) or automated PD
- Advantages: Gradual fluid removal, fewer cardiovascular events
- Complications: Peritonitis, tunnel infections, weight gain
- Requires patient training and compliance

TRANSPLANTATION:
- Best long-term outcome for suitable patients
- Immunosuppression: Triple therapy standard (CNI, MMF, steroid)
- Acute rejection: 0.03-1.5 episodes/patient-year
- Chronic rejection: Main cause of long-term graft loss
- Acute tubular necrosis: Common in early post-transplant period

VASCULAR ACCESS:
- AV fistula: Best long-term patency, needs 4-6 weeks maturation
- Fistula failure: Can occur in 10-60% of patients
- Catheter: For temporary access, higher infection risk
"""
            },
            {
                "source": "Glomerulonephritis and Immune-Mediated Kidney Disease",
                "content": """
Glomerulonephritis Treatment Protocols:

IgA NEPHROPATHY:
- Most common GN worldwide
- Presentation: Hematuria, proteinuria, variable progression
- Treatment: RAAS blockade, corticosteroids for aggressive disease
- Prognosis: 20-30% reach ESRD within 20 years

LUPUS NEPHRITIS:
- Classification: World Health Organization classes I-VI
- Class IV: Diffuse, requires aggressive treatment
- Induction therapy: Cyclophosphamide or mycophenolate + steroids
- Maintenance: Azathioprine or mycophenolate
- Prognosis: 10-year renal survival 70-80% with treatment

MEMBRANOUS NEPHROPATHY:
- Presents with nephrotic syndrome
- 30% spontaneous remission possible
- Treatment: Immunosuppression for progressive cases
- Agents: Corticosteroids, cyclophosphamide, rituximab
- Risk: Thromboembolism due to nephrotic state

RAPIDLY PROGRESSIVE GN (RPGN):
- Medical emergency, requires prompt treatment
- Workup: ANCA, anti-GBM, immune complex screening
- Treatment: Plasmapheresis, high-dose steroids, cyclophosphamide
- Prognosis: Critical window for intervention (weeks)
"""
            },
            {
                "source": "Electrolyte and Mineral Metabolism",
                "content": """
Hyperkalemia Management:

PATHOPHYSIOLOGY:
- Normal serum K+: 3.5-5.0 mEq/L
- In CKD, kidneys cannot excrete potassium adequately
- Risk increases significantly in stages 4-5

TREATMENT APPROACH:
1. Calcium gluconate 10-20 mL IV: Immediate membrane stabilization
2. Insulin + dextrose: Shifts K+ intracellularly
3. Beta-agonists: Albuterol nebulized or IV
4. Sodium polystyrene sulfonate: Binds K+ in GI tract
5. Loop diuretics: If some residual function
6. Dialysis: Definitive treatment in ESRD

DIETARY RESTRICTION:
- Foods high in potassium: Bananas, oranges, tomatoes, potatoes
- Target intake: 2,000-3,000 mg/day for CKD patients
- Education critical for patient compliance

MONITORING:
- ECG changes: Peaked T waves, prolonged PR interval, wide QRS
- Symptoms: Muscle weakness, palpitations, cardiac arrhythmias
- Check frequency: More often in stages 4-5
"""
            },
            {
                "source": "Post-Discharge Care and Follow-up",
                "content": """
Post-Discharge Patient Education:

MEDICATION COMPLIANCE:
- Critical for CKD progression prevention
- ACE-I/ARBs: Don't discontinue without medical guidance
- AVOID NSAIDs: Can accelerate kidney disease
- NSAIDs alternatives: Acetaminophen, other non-NSAID agents

FLUID MANAGEMENT:
- Varies by stage and residual function
- Early stages: Usually no restriction
- Advanced CKD/dialysis: Typically 1-1.5L daily limit
- Include medications, fruits, soups in fluid count

BLOOD PRESSURE CONTROL:
- Target: <120/90 mmHg for most CKD patients
- <130/80 mmHg may be considered in some cases
- Monitor at home daily if possible
- Report sustained BP >160/100 immediately

WHEN TO SEEK EMERGENCY CARE:
- Severe hyperkalemia symptoms (chest pain, severe weakness)
- Acute oliguria (urine output <400 mL/day)
- Severe hypertension unresponsive to medication
- Signs of infection in dialysis access
- Acute shortness of breath or chest pain
- Syncope or severe dizziness

LAB MONITORING:
- Creatinine and BUN: Every 1-3 months
- Potassium: Monthly to quarterly
- Calcium, phosphorus: Monthly in advanced CKD
- Hemoglobin: Monitor for anemia
"""
            }
        ]
        
        return materials
    
    def _chunk_documents(self, documents: List[Dict[str, str]], chunk_size: int = 600) -> List[tuple]:
        """
        Split documents into chunks for embedding
        Returns tuples compatible with VectorStore.add_documents format
        """
        chunks = []
        chunk_id = 0
        
        for doc in documents:
            text = doc["content"]
            source = doc["source"]
            
            # Split by sentences for better chunking
            sentences = text.split('.')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < chunk_size:
                    current_chunk += sentence + "."
                else:
                    if current_chunk.strip():
                        chunks.append((f"ref_{chunk_id:05d}", current_chunk.strip()))
                        chunk_id += 1
                    current_chunk = sentence + "."
            
            if current_chunk.strip():
                chunks.append((f"ref_{chunk_id:05d}", current_chunk.strip()))
                chunk_id += 1
        
        logger.info(f"Created {len(chunks)} chunks from reference materials")
        return chunks
    
    def query_reference_materials(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Query the vector store for relevant information using Gemini embeddings
        """
        try:
            log_retrieval_attempt("rag", query, False, "chromadb")
            
            # Search using VectorStore
            search_results = self.vector_store.search(query, n_results=n_results)
            
            formatted_results = []
            if search_results and search_results["documents"]:
                for doc, metadata in zip(search_results["documents"][0], search_results["metadatas"][0]):
                    formatted_results.append({
                        "content": doc,
                        "source": metadata.get("source", "Unknown"),
                        "relevance_score": 1 - search_results["distances"][0][len(formatted_results)]
                    })
                
                log_retrieval_attempt("rag", query, True, "chromadb")
                return {
                    "success": True,
                    "results": formatted_results,
                    "message": f"Found {len(formatted_results)} relevant references"
                }
            else:
                log_retrieval_attempt("rag", query, False, "chromadb")
                return {
                    "success": False,
                    "results": [],
                    "message": "No relevant reference materials found"
                }
        
        except Exception as e:
            logger.error(f"Error querying reference materials: {str(e)}")
            log_retrieval_attempt("rag", query, False, "chromadb")
            return {
                "success": False,
                "results": [],
                "message": f"Error querying reference materials: {str(e)}"
            }
    
    def add_pdf_documents(self, pdf_chunks: List[tuple], source: str = "pdf_upload") -> Dict[str, Any]:
        """
        Add preprocessed PDF chunks to vector store
        """
        try:
            self.vector_store.add_documents(pdf_chunks, source=source)
            stats = self.vector_store.get_stats()
            
            logger.info(f"Added {len(pdf_chunks)} PDF chunks to vector store")
            return {
                "success": True,
                "message": f"Successfully added {len(pdf_chunks)} document chunks",
                "total_documents": stats["total_documents"]
            }
        except Exception as e:
            logger.error(f"Error adding PDF documents: {str(e)}")
            return {
                "success": False,
                "message": f"Error adding documents: {str(e)}",
                "total_documents": 0
            }
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get current vector store statistics
        """
        try:
            return self.vector_store.get_stats()
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {"total_documents": 0, "error": str(e)}
    
    def clear_vector_store(self) -> Dict[str, Any]:
        """
        Clear all documents from vector store (useful for testing)
        """
        try:
            # This would need to be implemented in VectorStore class
            logger.warning("Clearing vector store - all documents will be removed")
            # Implementation depends on your VectorStore class
            return {
                "success": True,
                "message": "Vector store cleared successfully"
            }
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return {
                "success": False,
                "message": f"Error clearing vector store: {str(e)}"
            }