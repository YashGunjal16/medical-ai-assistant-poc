import os
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.db_tool import retrieve_patient_data
from app.utils.logger import log_interaction, log_agent_handoff
from app.utils.model_config import get_available_model

class ReceptionistAgent:
    """
    Receptionist Agent - Greets patients and retrieves their discharge reports
    Routes medical queries to Clinical Agent
    """
    
    def __init__(self):
        model_name = get_available_model()
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        self.name = "Receptionist Agent"
    
    def greet_and_retrieve(self, patient_name: str) -> Dict[str, Any]:
        """Greet patient and retrieve their discharge report"""
        
        # Retrieve patient data from database
        retrieval_result = retrieve_patient_data(patient_name)
        
        if not retrieval_result["success"]:
            response_text = f"I'm sorry, I couldn't find a discharge report for {patient_name} in our system. Could you please verify the name or try again?"
            log_interaction(patient_name, self.name, patient_name, response_text, "greeting_failed")
            
            return {
                "success": False,
                "message": response_text,
                "patient_data": None
            }
        
        patient_data = retrieval_result["patient_data"]
        
        # Generate personalized greeting
        greeting_prompt = f"""
You are a friendly medical receptionist. A patient named {patient_name} has just started their post-discharge check-in.
        
Their discharge report shows:
- Diagnosis: {patient_data['primary_diagnosis']}
- Discharge Date: {patient_data['discharge_date']}
- Age: {patient_data['age']}

Generate a warm, professional greeting that:
1. Welcomes them back
2. Acknowledges their diagnosis
3. Asks how they're feeling
4. Invites them to share any concerns

Keep it concise (2-3 sentences).
"""
        
        greeting_response = self.llm.invoke(greeting_prompt)
        greeting_text = greeting_response.content
        
        log_interaction(patient_name, self.name, f"Greeted patient {patient_name}", greeting_text, "greeting")
        
        return {
            "success": True,
            "message": greeting_text,
            "patient_data": patient_data,
            "formatted_report": retrieval_result["formatted_report"]
        }
    
    def handle_patient_input(self, patient_name: str, patient_input: str, patient_data: Dict) -> Dict[str, Any]:
        """
        Handle patient input and decide whether to:
        1. Answer as receptionist
        2. Route to Clinical Agent
        """
        
        # Check if input contains medical concerns that need clinical expertise
        medical_keywords = [
            "symptom", "pain", "swelling", "breathing", "shortness of breath",
            "medication", "side effect", "should i", "worried", "concern",
            "warning", "blood", "urine", "fever", "dizzy", "chest"
        ]
        
        needs_clinical_agent = any(keyword in patient_input.lower() for keyword in medical_keywords)
        
        if needs_clinical_agent:
            # Log handoff and return indication for routing
            log_agent_handoff(self.name, "Clinical Agent", f"Patient has medical concerns: {patient_input[:50]}", patient_name)
            
            return {
                "success": True,
                "route_to_clinical": True,
                "message": "I understand you have a medical concern. Let me connect you with our Clinical AI Agent who can provide guidance based on your specific diagnosis and medications.",
                "patient_input": patient_input
            }
        
        # Handle non-medical questions as receptionist
        receptionist_prompt = f"""
You are a helpful medical receptionist. A patient named {patient_name} with diagnosis: {patient_data['primary_diagnosis']} has asked:

"{patient_input}"

Provide a helpful, empathetic response as a receptionist. If they're asking about:
- Appointment scheduling: Refer them to their follow-up date
- General well-being: Encourage them
- Medication questions: Suggest they contact their doctor

Keep response concise and professional.
"""
        
        response = self.llm.invoke(receptionist_prompt)
        response_text = response.content
        
        log_interaction(patient_name, self.name, patient_input, response_text, "receptionist_response")
        
        return {
            "success": True,
            "route_to_clinical": False,
            "message": response_text
        }
