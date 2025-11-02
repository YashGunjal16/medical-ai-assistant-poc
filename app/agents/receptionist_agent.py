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
            google_api_key=os.getenv("GOOGLE_API_KEY"),
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
        
        patient_input_lower = patient_input.lower()
        
        # STEP 1: Check for explicit RECEPTIONIST-only queries first
        receptionist_only_patterns = [
            # Greetings/pleasantries
            "thank", "thanks", "appreciate", "grateful",
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "goodbye", "bye", "see you", "take care",
            
            # Administrative
            "appointment time", "when is my appointment", "reschedule",
            "clinic hours", "clinic address", "contact information",
            "billing", "insurance", "cost", "payment",
            "directions to", "how do i get to", "where is",
            "what to bring", "bring to appointment",
            
            # Non-medical requests
            "update my", "change my contact", "phone number",
            "copy of discharge", "medical records"
        ]
        
        is_receptionist_query = any(pattern in patient_input_lower for pattern in receptionist_only_patterns)
        
        # STEP 2: Check for explicit CLINICAL keywords
        clinical_keywords = [
            # Symptoms
            "symptom", "pain", "ache", "sore", "hurt", "hurting",
            "swelling", "swollen", "swallowed", "edema", "bloated",
            
            # Vital signs/measurements
            "fever", "temperature", "blood pressure", "weight loss", "weight gain",
            "breathing problem", "shortness", "dizzy", "dizziness", "nausea",
            "vomit", "vomiting", "diarrhea",
            
            # Body parts (in context of problems)
            "chest pain", "leg pain", "stomach pain", "abdomen", "back pain",
            
            # Medical concerns
            "medication side", "drug interaction", "side effect",
            "should i take", "stop taking", "worried about my",
            "concerned about my", "is it normal to",
            
            # Disease-specific
            "kidney", "urine color", "blood in", "protein in",
            "creatinine", "dialysis",
            
            # Clinical guidance
            "precaution", "avoid eating", "warning sign", "emergency",
            "when to call doctor", "medical advice", "health concern"
        ]
        
        has_clinical_keywords = any(keyword in patient_input_lower for keyword in clinical_keywords)
        
        # STEP 3: Decision logic with priority
        
        # If it's clearly a receptionist query, handle it regardless of other factors
        if is_receptionist_query and not has_clinical_keywords:
            # Handle non-medical questions as receptionist
            receptionist_prompt = f"""
You are a helpful medical receptionist. A patient named {patient_name} with diagnosis: {patient_data['primary_diagnosis']} has said:

"{patient_input}"

Provide a brief, warm, and helpful response as a receptionist. 

If they're asking about:
- Appointment details: Their follow-up is {patient_data['follow_up']}
- What to bring: Suggest standard items (insurance card, ID, medication list, questions)
- Greetings/thanks: Respond warmly and professionally
- Scheduling: Suggest they contact the clinic directly

Keep response concise (2-3 sentences) and friendly.
"""
            
            response = self.llm.invoke(receptionist_prompt)
            response_text = response.content
            
            log_interaction(patient_name, self.name, patient_input, response_text, "receptionist_response")
            
            return {
                "success": True,
                "route_to_clinical": False,
                "message": response_text
            }
        
        # If it has clinical keywords, route to clinical agent
        if has_clinical_keywords:
            log_agent_handoff(self.name, "Clinical Agent", f"Patient has medical concerns: {patient_input[:50]}", patient_name)
            
            return {
                "success": True,
                "route_to_clinical": True,
                "message": "I understand you have a medical concern. Let me connect you with our Clinical AI Agent who can provide guidance based on your specific diagnosis and medications.",
                "patient_input": patient_input
            }
        
        # STEP 4: For ambiguous cases, use LLM classification
        if len(patient_input.split()) > 5:
            classification_prompt = f"""
Classify this patient message as either CLINICAL or ADMINISTRATIVE.

Patient diagnosis: {patient_data['primary_diagnosis']}
Message: "{patient_input}"

CLINICAL messages include:
- Symptoms, pain, or health changes
- Questions about medications or side effects
- Disease-specific medical questions
- Warning signs or complications
- Medical advice requests

ADMINISTRATIVE messages include:
- Appointment scheduling/logistics
- Thank you messages and pleasantries
- Clinic information requests
- Non-medical administrative matters
- What to bring to appointments (unless asking about specific medical tests)

Respond with ONLY one word: CLINICAL or ADMINISTRATIVE
"""
            
            classification_response = self.llm.invoke(classification_prompt)
            classification = classification_response.content.strip().upper()
            
            if "CLINICAL" in classification:
                log_agent_handoff(self.name, "Clinical Agent", f"Patient has medical concerns: {patient_input[:50]}", patient_name)
                
                return {
                    "success": True,
                    "route_to_clinical": True,
                    "message": "I understand you have a medical concern. Let me connect you with our Clinical AI Agent who can provide guidance based on your specific diagnosis and medications.",
                    "patient_input": patient_input
                }
        
        # Default: Handle as receptionist
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