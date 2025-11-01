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
    Provides citations and educational information
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
        if rag_results["success"] and rag_results["results"]:
            rag_context = "Reference Material Findings:\n"
            for result in rag_results["results"]:
                rag_context += f"\nSource: {result['source']}\n{result['content'][:300]}...\n"
        
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

DISCLAIMER: This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice.

Please provide:
1. Educational information relevant to their diagnosis and query
2. Any warnings or precautions mentioned in reference materials
3. Recommendation to seek professional medical care if needed
4. Citations from reference materials used
"""
        
        # Generate response using LLM
        clinical_response = self.llm.invoke(clinical_context)
        response_text = clinical_response.content
        
        # If RAG didn't find sufficient info, offer web search
        web_search_offered = False
        if not rag_results["success"] and "latest" in patient_input.lower():
            web_results = self.web_search.search(patient_input, max_results=2)
            if web_results["success"] and web_results["results"]:
                web_info = "\n\nWEB SEARCH RESULTS (Recent Information):\n"
                for result in web_results["results"]:
                    web_info += f"- {result['title']}: {result['snippet'][:150]}...\n"
                response_text += web_info
                web_search_offered = True
        
        log_interaction(patient_name, self.name, patient_input, response_text, "clinical_response")
        
        return {
            "success": True,
            "message": response_text,
            "rag_used": rag_results["success"],
            "web_search_used": web_search_offered,
            "disclaimer": "This is an AI assistant for educational purposes only. Always consult healthcare professionals for medical advice."
        }
