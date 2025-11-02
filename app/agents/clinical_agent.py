import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.rag_tool import RAGManager
from app.tools.web_search_tool import WebSearchTool
from app.utils.logger import log_interaction
from app.utils.model_config import get_available_model

class ClinicalAgent:
    """
    Clinical AI Agent - Handles medical queries using RAG and web search
    and educational information with clear source indicators
    """
    
    def __init__(self):
        model_name = get_available_model()
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.5,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.rag_manager = RAGManager()
        self.web_search = WebSearchTool()
        self.name = "Clinical Agent"
    
    def handle_medical_query(self, patient_name: str, patient_input: str, patient_data: Dict) -> Dict[str, Any]:
        """
        Handle medical queries with RAG and web search
        """
        
        # First, try RAG retrieval
        rag_results = self.rag_manager.query_reference_materials(patient_input, n_results=3)
        
        # Build context from RAG results
        rag_context = ""
        rag_sources = []  # NEW: Track RAG sources
        if rag_results["success"] and rag_results["results"]:
            rag_context = "Reference Material Findings:\n"
            for idx, result in enumerate(rag_results["results"], 1):  # CHANGED: Added enumeration
                rag_context += f"\n[Reference {idx}] {result['content'][:400]}...\n"  # CHANGED: Increased content length and added reference number
                rag_sources.append(result.get('source', 'Medical Reference Database'))  # NEW: Collect sources
        
        # Prepare clinical context from patient data
        clinical_context = f"""
PATIENT INFORMATION:
- Name: {patient_name}
- Age: {patient_data['age']}
- Primary Diagnosis: {patient_data['primary_diagnosis']}
- Current Medications: {', '.join(patient_data['medications'])}
- Dietary Restrictions: {patient_data['dietary_restrictions']}
- Warning Signs: {patient_data['warning_signs']}
- Follow-up: {patient_data['follow_up']}

PATIENT'S QUERY: {patient_input}

{"RELEVANT REFERENCE MATERIALS:\n" + rag_context if rag_context else ""}

IMPORTANT INSTRUCTIONS:  # NEW SECTION
1. Provide educational information relevant to their diagnosis and query
2. Include any warnings or precautions from reference materials
3. Recommend seeking professional medical care if needed
4. DO NOT include specific citations, page numbers, or quoted text
5. DO NOT reproduce exact text from sources
6. Summarize information in your own words
7. Keep the response clear, concise, and patient-friendly

DISCLAIMER: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.
"""
        
        # Generate response using LLM
        clinical_response = self.llm.invoke(clinical_context)
        response_text = clinical_response.content
        
        # NEW: Remove any citation artifacts that might slip through
        response_text = self._clean_citations(response_text)
        
        # CHANGED: Better web search logic and tracking
        web_search_used = False  # RENAMED from web_search_offered
        web_sources = []  # NEW: Track web sources
        if "latest" in patient_input.lower() or "recent" in patient_input.lower() or not rag_results["success"]:  # CHANGED: Added more trigger words
            web_results = self.web_search.search(patient_input, max_results=2)
            if web_results["success"] and web_results["results"]:
                web_info = "\n\n📱 **Additional Information from Recent Sources:**\n"  # CHANGED: Added emoji and better formatting
                for result in web_results["results"]:
                    web_info += f"• {result['snippet'][:200]}...\n"  # CHANGED: Increased snippet length and bullet points
                    web_sources.append(result.get('title', 'Web Source'))  # NEW: Collect web sources
                response_text += web_info
                web_search_used = True  # CHANGED: Renamed variable
        
        # NEW: Add source information at the end
        source_info = self._format_sources(rag_sources, web_sources)
        if source_info:
            response_text += f"\n\n{source_info}"
        
        # NEW: Add disclaimer at the end
        response_text += "\n\n⚠️ **Disclaimer:** This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice."
        
        log_interaction(patient_name, self.name, patient_input, response_text, "clinical_response")
        
        return {
            "success": True,
            "message": response_text,
            "rag_used": rag_results["success"],
            "web_search_used": web_search_used  # CHANGED: Renamed from web_search_offered
            # REMOVED: "disclaimer" key from return dict since it's now in the message
        }
    
    # NEW METHOD
    def _clean_citations(self, text: str) -> str:
        """Remove citation artifacts from response"""
        import re
        
        # Remove patterns like (Source: pdf, page X)
        text = re.sub(r'\(Source:.*?\)', '', text)
        
        # Remove patterns like [Source: ...]
        text = re.sub(r'\[Source:.*?\]', '', text)
        
        # Remove "Citations from reference materials used:" section
        if "Citations from reference materials used:" in text or "Citations from Reference Materials Used:" in text:
            text = re.split(r'Citations from [Rr]eference [Mm]aterials [Uu]sed:', text)[0]
        
        # Remove numbered citation sections like "4. Citations..."
        text = re.sub(r'\n\d+\.\s*Citations.*$', '', text, flags=re.MULTILINE | re.DOTALL)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    # NEW METHOD
    def _format_sources(self, rag_sources: list, web_sources: list) -> str:
        """Format source information"""
        source_text = ""
        
        if rag_sources:
            source_text += "📚 **Information Source:** Medical Reference Database (Vector DB)"
        
        if web_sources:
            if source_text:
                source_text += "\n"
            source_text += "🌐 **Additional Sources:** Web Search"
        
        return source_text