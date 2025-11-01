# Medical AI POC - Complete Workflow Examples

## Overview
This document provides step-by-step demonstrations of the Medical AI Assistant in action. Each scenario shows real patient interactions with the system's dual-agent architecture.

---

## Scenario 1: Initial Patient Greeting & Discharge Report Retrieval

### Patient: John Smith (P001) - CKD Stage 3

**Step 1: Patient Initiates Session**
\`\`\`
User Input: "Hello, I'm John Smith"
\`\`\`

**Step 2: Backend Processing**
- Receptionist Agent receives greeting
- Patient database lookup: P001
- Discharge report retrieved

**Step 3: System Response**
\`\`\`
API Response:
{
  "success": true,
  "message": "Hi John! I found your discharge report from January 15th for Chronic Kidney Disease Stage 3. 
             Welcome back! How are you feeling today? Are you following your medication schedule?",
  "session_id": "John_Smith_1704067200.5",
  "patient_data": {
    "name": "John Smith",
    "diagnosis": "Chronic Kidney Disease Stage 3",
    "age": 58,
    "discharge_date": "2024-01-15"
  }
}
\`\`\`

**Agents Involved:**
- Receptionist Agent: ✓ Greeting & retrieval
- Clinical Agent: ✗ Not needed

**Logging:**
\`\`\`
[2024-01-20 10:15:23] INFO - New session created for patient: John Smith (Session: John_Smith_1704067200.5)
[2024-01-20 10:15:23] INFO - [Receptionist Agent] Patient data retrieved for John Smith
\`\`\`

---

## Scenario 2: Medical Query Routing - Agent Handoff

### Patient: John Smith - Reporting Symptoms

**Step 1: Patient Reports Concern**
\`\`\`
User Input: "I'm having swelling in my legs and feel very tired. Is this normal after discharge?"
\`\`\`

**Step 2: Receptionist Agent Analysis**
- Input contains medical terms: "swelling", "tired"
- Pattern matches clinical concern keywords
- Decision: Route to Clinical Agent

**Step 3: Clinical Agent Response (With RAG)**
\`\`\`
API Response:
{
  "success": true,
  "response": "Based on your CKD Stage 3 diagnosis and nephrology guidelines, leg swelling 
             and fatigue can indicate several concerns:

             1. FLUID RETENTION: Common in CKD due to salt accumulation. Check if:
                - You're following the 2g/day sodium restriction
                - Your fluid intake is limited to 1.5L/day
                - Your Furosemide dosage is correct

             2. ANEMIA: CKD often causes reduced red blood cell production. Symptoms include:
                - Persistent fatigue
                - Shortness of breath
                - Weakness

             3. WARNING SIGNS - Seek immediate medical attention if:
                - Swelling is severe or sudden
                - You experience shortness of breath
                - You have decreased urine output
                - Symptoms worsen rapidly

             MEDICAL DISCLAIMER: This is an AI assistant for educational purposes only. 
             Always consult healthcare professionals for medical advice.

             RECOMMENDATION: Monitor your symptoms and contact your nephrologist immediately 
             if they worsen. Your follow-up appointment is in 2 weeks.",
  "agent_used": "Clinical Agent",
  "session_id": "John_Smith_1704067200.5"
}
\`\`\`

**Agents Involved:**
- Receptionist Agent: ✓ Initial analysis & routing decision
- Clinical Agent: ✓ Medical analysis with RAG retrieval
- RAG System: ✓ Retrieved nephrology guidelines

**Logging:**
\`\`\`
[2024-01-20 10:18:45] INFO - [Receptionist Agent] Patient input analyzed
[2024-01-20 10:18:45] INFO - Route decision: CLINICAL - Medical concern detected
[2024-01-20 10:18:47] INFO - [Clinical Agent] Processing medical query for John Smith
[2024-01-20 10:18:47] INFO - RAG retrieval: 3 relevant documents found
[2024-01-20 10:18:48] INFO - Medical response generated using Gemini-1.5-pro
\`\`\`

---

## Scenario 3: Web Search Fallback - Recent Research Query

### Patient: Emily Rodriguez (P004) - Diabetic Nephropathy

**Step 1: Patient Asks About New Treatment**
\`\`\`
User Input: "I read about SGLT2 inhibitors for kidney disease. Can I use them? 
           Are they effective for my type of diabetes and kidney disease?"
\`\`\`

**Step 2: Clinical Agent Processing**
- Query contains specific medication: "SGLT2 inhibitors"
- Patient condition: Diabetic Nephropathy Stage 3b
- RAG search: Limited recent data (May 2023)
- Decision: Use web search for latest research

**Step 3: Web Search + Clinical Response**
\`\`\`
API Response:
{
  "success": true,
  "response": "Excellent question about SGLT2 inhibitors for your Diabetic Nephropathy!

             LATEST RESEARCH (2024):
             According to recent medical literature and clinical trials:

             1. EFFECTIVENESS FOR YOUR CONDITION:
                - SGLT2 inhibitors (like Empagliflozin, which you're already on!)
                - Reduce proteinuria by 30-40% in diabetic nephropathy
                - Slow GFR decline by 29% vs placebo
                - Reduce cardiovascular events
                
             2. YOUR CURRENT SITUATION:
                - You're already taking Empagliflozin 10mg daily
                - This is well-suited for Stage 3b CKD with diabetes
                - Consider dose optimization if tolerated
                
             3. BENEFITS SPECIFIC TO YOUR PROFILE:
                - Blood glucose control improvement
                - Weight reduction (7-9 lbs average)
                - Blood pressure reduction (2-4 mmHg)
                - Kidney protection
                
             4. MONITORING REQUIRED:
                - Kidney function (creatinine, GFR) every 3 months
                - Blood glucose monitoring
                - Watch for genital infections
                
             MEDICAL DISCLAIMER: This is an AI assistant for educational purposes only. 
             Always consult healthcare professionals for medical advice.

             SOURCE: PubMed Central, ADA Guidelines 2024, Kidney Disease: Improving Global 
             Outcomes (KDIGO)
             
             RECOMMENDATION: Discuss with your endocrinologist and nephrologist about 
             optimizing your current SGLT2 inhibitor dosage during your upcoming visits.",
  "agent_used": "Clinical Agent with Web Search",
  "sources": [
    "https://pubmed.ncbi.nlm.nih.gov/2024-sglt2-inhibitors",
    "https://kidney.org/diabetic-nephropathy-2024",
    "https://ada.org/guidelines-2024"
  ],
  "session_id": "Emily_Rodriguez_1704067200.8"
}
\`\`\`

**Agents Involved:**
- Clinical Agent: ✓ Query analysis
- RAG System: ✓ Initial knowledge check
- Web Search: ✓ Recent research retrieval
- Gemini-1.5-pro: ✓ Synthesized response

**Logging:**
\`\`\`
[2024-01-20 11:22:15] INFO - [Clinical Agent] Processing query for Emily Rodriguez
[2024-01-20 11:22:15] INFO - RAG search: 2 documents with limited recent data
[2024-01-20 11:22:15] INFO - Web search triggered for: SGLT2 inhibitors diabetic nephropathy 2024
[2024-01-20 11:22:18] INFO - Retrieved 5 web sources
[2024-01-20 11:22:20] INFO - Response synthesized with latest research
\`\`\`

---

## Scenario 4: Patient Data Retrieval & Medication Management

### Patient: Robert Williams (P005) - CKD Stage 4 Pre-Dialysis

**Step 1: Patient Asks About Medications**
\`\`\`
User Input: "What medications am I taking and why? I'm confused about all these pills."
\`\`\`

**Step 2: Receptionist Agent (Knowledge Base Lookup)**
- Query type: Information retrieval (not medical advice)
- Action: Patient database lookup
- Retrieve medication list and education

**Step 3: Response with Patient Education**
\`\`\`
API Response:
{
  "success": true,
  "response": "Great question! Understanding your medications is important. Here's your 
             current medication plan for CKD Stage 4:

             YOUR MEDICATIONS (from discharge: Jan 13, 2024):

             1. CALCITRIOL 0.5mcg twice daily
                WHY: Active vitamin D for bone health
                - CKD reduces vitamin D activation
                - Prevents bone disease and secondary hyperparathyroidism
                - TAKE WITH: Meals for better absorption
                
             2. SEVELAMER (Phosphate Binder)
                WHY: Controls phosphorus levels
                - High phosphorus damages bones and blood vessels
                - Take with each meal
                - Do NOT take with other medications (separate by 2-4 hours)
                
             3. ADDITIONAL MEDICATIONS (in preparation for dialysis):
                - Iron supplements (if needed)
                - Erythropoietin (if anemia develops)
                
             IMPORTANT DIET NOTES:
                - STRICT POTASSIUM restriction: Avoid bananas, oranges, tomatoes
                - STRICT PHOSPHORUS restriction: Limit dairy, nuts, seeds
                - STRICT SODIUM: Max 2g/day (high salt foods)
                - Fluid restriction: As ordered by your nephrologist
                
             MEDICAL DISCLAIMER: This is an AI assistant for educational purposes only. 
             Always consult healthcare professionals for medical advice.

             WARNING SIGNS REQUIRING IMMEDIATE CARE:
                - Severe itching (possible uremia)
                - Irregular heartbeat (hyperkalemia)
                - Confusion (uremic syndrome)
                - Bone pain
                
             Your nephrology appointment is scheduled weekly.",
  "agent_used": "Receptionist Agent",
  "session_id": "Robert_Williams_1704067200.12"
}
\`\`\`

**Agents Involved:**
- Receptionist Agent: ✓ Medication lookup & education
- Patient Database: ✓ Retrieved medication information
- Clinical Agent: ✗ Not needed (informational query)

---

## Scenario 5: Complex Medical Decision Support - Post-Transplant

### Patient: Patricia Martinez (P006) - Post-Transplant Monitoring

**Step 1: Patient with Multiple Concerns**
\`\`\`
User Input: "I had a slight fever yesterday (100.2F), and I noticed my urine output 
           decreased. Also, I feel some discomfort near the transplant site. 
           Should I stop my immunosuppressants?"
\`\`\`

**Step 2: Clinical Agent Analysis**
- Query complexity: HIGH (multiple symptoms + medication decision)
- Patient status: Post-transplant (immunocompromised)
- Severity: Potential rejection indicators
- Decision: URGENT - Route to clinical with strong disclaimer

**Step 3: Urgent Clinical Response**
\`\`\`
API Response:
{
  "success": true,
  "response": "URGENT MEDICAL ATTENTION REQUIRED

             ⚠️ CRITICAL DISCLAIMER: This is an AI assistant for educational purposes only. 
             Your symptoms require IMMEDIATE medical evaluation by your transplant team. 
             DO NOT DELAY - Contact your transplant center NOW or go to the emergency room.

             YOUR SYMPTOMS SUGGEST POSSIBLE TRANSPLANT REJECTION:

             1. FEVER (100.2°F)
                - Potential sign of infection or rejection
                - Monitor for increase above 100.4°F

             2. DECREASED URINE OUTPUT
                - May indicate graft dysfunction
                - Should be tracked carefully
                - Compare to your baseline

             3. DISCOMFORT AT TRANSPLANT SITE
                - Could indicate rejection or infection
                - Requires urgent evaluation

             ⚠️ CRITICAL: DO NOT STOP IMMUNOSUPPRESSANTS
                - Never stop Tacrolimus or Mycophenolate without medical supervision
                - Sudden discontinuation causes rejection within days
                - Missing even one dose can be dangerous

             IMMEDIATE ACTIONS:
                1. Contact your transplant center now
                2. Provide them this information:
                   - Temperature: 100.2°F
                   - Urine output: Decreased
                   - Discomfort: Transplant site
                   - Current medications: Tacrolimus 2mg BID, Mycophenolate 500mg BID

                3. Go to ER if you cannot reach transplant center

             EXPECTED TIMELINE:
                - Urgent labs needed: Creatinine, BUN, Tacrolimus level
                - Possible ultrasound of graft
                - Possible biopsy if rejection suspected

             Your transplant appointment is in 3 days - this cannot wait that long.
             SEEK CARE IMMEDIATELY.",
  "agent_used": "Clinical Agent - URGENT",
  "urgency_level": "HIGH",
  "escalation_required": true,
  "session_id": "Patricia_Martinez_1704067200.6"
}
\`\`\`

**Agents Involved:**
- Clinical Agent: ✓ Symptom analysis with urgency detection
- Medical Knowledge: ✓ Transplant rejection protocols
- Safety System: ✓ Strong disclaimers & escalation

**Logging:**
\`\`\`
[2024-01-20 14:35:22] INFO - [Clinical Agent] Analyzing post-transplant symptoms for Patricia Martinez
[2024-01-20 14:35:22] ALERT - URGENT: Potential transplant rejection indicators detected
[2024-01-20 14:35:23] ALERT - Escalation flag set: IMMEDIATE MEDICAL ATTENTION REQUIRED
[2024-01-20 14:35:24] INFO - Strong medical disclaimer added
[2024-01-20 14:35:24] INFO - Emergency action items provided
\`\`\`

---

## Scenario 6: Session History & Multi-Turn Conversation

### Patient: Sarah Johnson (P002) - CKD Stage 2 with Hypertension

**First Message: Day 1**
\`\`\`
User Input: "Hi, I'm Sarah Johnson. I was discharged from the hospital."
Response: [Greeting and data retrieval - Session created]
\`\`\`

**Second Message: Day 1 - 30 minutes later**
\`\`\`
User Input: "What should I eat? I'm confused about the diabetic diet."
Agent Used: Receptionist
Response: [Dietary guidance for CKD Stage 2 + diabetes]
\`\`\`

**Third Message: Day 2**
\`\`\`
User Input: "My blood pressure was 155/95 this morning. Is that okay?"
Agent Used: Clinical Agent (medical concern)
Response: [BP analysis with medication review]
\`\`\`

**System Session Report:**
\`\`\`
GET /api/session/Sarah_Johnson_1704067200.2

Response:
{
  "success": true,
  "session_id": "Sarah_Johnson_1704067200.2",
  "patient_name": "Sarah Johnson",
  "created_at": "2024-01-20T10:15:23",
  "interactions_count": 3,
  "interactions": [
    {
      "timestamp": "2024-01-20T10:15:23",
      "agent": "Receptionist Agent",
      "user_input": "Hi, I'm Sarah Johnson. I was discharged from the hospital.",
      "response": "Hi Sarah! I found your discharge report from January 16th for Hypertension 
                  with CKD Stage 2..."
    },
    {
      "timestamp": "2024-01-20T10:45:12",
      "agent": "Receptionist Agent",
      "user_input": "What should I eat? I'm confused about the diabetic diet.",
      "response": "For your CKD Stage 2 with diabetes, here are dietary guidelines..."
    },
    {
      "timestamp": "2024-01-20T11:20:35",
      "agent": "Clinical Agent",
      "user_input": "My blood pressure was 155/95 this morning. Is that okay?",
      "response": "Your blood pressure reading is elevated. For CKD Stage 2..."
    }
  ]
}
\`\`\`

---

## Scenario 7: System Status & Admin Monitoring

### Admin Check: Active Sessions & Logs

**API Call: List All Active Sessions**
\`\`\`
GET /api/sessions/list

Response:
{
  "success": true,
  "total_sessions": 5,
  "sessions": [
    {
      "session_id": "John_Smith_1704067200.5",
      "patient_name": "John Smith",
      "created_at": "2024-01-20T10:15:23",
      "interaction_count": 4
    },
    {
      "session_id": "Emily_Rodriguez_1704067200.8",
      "patient_name": "Emily Rodriguez",
      "created_at": "2024-01-20T10:35:45",
      "interaction_count": 3
    },
    {
      "session_id": "Robert_Williams_1704067200.12",
      "patient_name": "Robert Williams",
      "created_at": "2024-01-20T11:22:15",
      "interaction_count": 2
    },
    {
      "session_id": "Patricia_Martinez_1704067200.6",
      "patient_name": "Patricia Martinez",
      "created_at": "2024-01-20T14:35:22",
      "interaction_count": 1
    },
    {
      "session_id": "Sarah_Johnson_1704067200.2",
      "patient_name": "Sarah Johnson",
      "created_at": "2024-01-20T15:10:33",
      "interaction_count": 1
    }
  ]
}
\`\`\`

**API Call: System Logs**
\`\`\`
GET /api/logs

Response (Last 20 entries):
{
  "success": true,
  "log_count": 50,
  "logs": [
    "[2024-01-20 15:18:33] INFO - New session created for patient: Sarah Johnson",
    "[2024-01-20 15:18:35] INFO - [Receptionist Agent] Patient data retrieved",
    "[2024-01-20 14:35:24] ALERT - URGENT: Potential transplant rejection indicators",
    "[2024-01-20 14:35:22] INFO - [Clinical Agent] Analyzing post-transplant symptoms",
    "[2024-01-20 11:22:20] INFO - Response synthesized with latest research",
    "[2024-01-20 11:22:18] INFO - Retrieved 5 web sources",
    "... (additional log entries) ..."
  ]
}
\`\`\`

---

## System Architecture During Workflows

\`\`\`
┌─────────────────────────────────────────────────────────────────┐
│                     PATIENT INPUT                                │
│                  (Streamlit Frontend)                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │   FastAPI Backend        │
         │  /api/chat endpoint      │
         └────────────┬─────────────┘
                      │
         ┌────────────┴──────────────┐
         ▼                           ▼
    ┌─────────────┐          ┌────────────────┐
    │ Receptionist│          │ Patient        │
    │ Agent       │          │ Database       │
    └────┬────────┘          └────────────────┘
         │
    Routing Decision
         │
    ┌────┴──────────────────┐
    ▼                       ▼
Info Query          Medical Concern?
    │                       │
    │                   ┌───▼────────┐
    │                   │ Clinical   │
    │                   │ Agent      │
    │                   └───┬────────┘
    │                       │
    │              ┌────────┴──────────┐
    │              ▼                   ▼
    │         RAG Query          Web Search
    │         (ChromaDB)         (Google API)
    │              │                   │
    │              └────────┬──────────┘
    │                       ▼
    │              Gemini 1.5 Pro
    │              (Generate Response)
    │                       │
    └───────────┬───────────┘
                ▼
         ┌─────────────────┐
         │ Logger          │
         │ (Track all)     │
         └─────────────────┘
                │
                ▼
         ┌──────────────────┐
         │ JSON Response    │
         │ to Frontend      │
         └──────────────────┘
\`\`\`

---

## Key Takeaways

1. **Dual-Agent Design**: Receptionist handles greetings and routing; Clinical Agent handles medical queries
2. **RAG + Web Search**: Local knowledge + latest research for comprehensive answers
3. **Medical Safety**: Strong disclaimers on all medical responses
4. **Session Management**: Complete conversation history and patient tracking
5. **Urgency Detection**: System identifies critical symptoms and escalates appropriately
6. **Comprehensive Logging**: Every interaction tracked for audit and monitoring

---

## Running These Examples

### In Streamlit:
1. Start backend: `uvicorn app.main:app --reload`
2. Start Streamlit: `streamlit run frontend/streamlit_app.py`
3. Select patient from dropdown
4. Follow conversation flow

### Using cURL (Backend):
\`\`\`bash
# 1. Greet patient
curl -X POST http://localhost:8000/api/greet \
  -H "Content-Type: application/json" \
  -d '{"patient_name": "John Smith"}'

# 2. Ask question (use session_id from response)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Smith",
    "session_id": "YOUR_SESSION_ID",
    "query": "I have swelling in my legs"
  }'
\`\`\`

---

## Notes for Demonstration

- Responses are AI-generated but follow medical guidelines
- All patient data is dummy/fictional
- System uses Gemini 1.5 Pro for natural language processing
- RAG system includes nephrology reference materials
- Web search provides latest research context
- All responses include appropriate medical disclaimers
