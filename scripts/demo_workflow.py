"""
Medical AI POC - Complete Workflow Demo Script
Demonstrates all system capabilities with realistic patient scenarios
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any
import sys

# Configuration
BACKEND_URL = "http://localhost:8000"
DEMO_DELAY = 2  # seconds between API calls for readability

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DemoWorkflow:
    """Execute complete Medical AI POC workflows"""
    
    def __init__(self, backend_url: str = BACKEND_URL):
        self.backend_url = backend_url
        self.sessions = {}
        self.demo_results = {
            "total_scenarios": 0,
            "passed": 0,
            "failed": 0,
            "scenarios": []
        }
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")
    
    def print_section(self, text: str):
        """Print formatted section"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}► {text}{Colors.END}")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.END}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.END}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ {text}{Colors.END}")
    
    def print_response(self, response: Dict[Any, Any], max_length: int = 200):
        """Pretty print API response"""
        print(f"{Colors.YELLOW}Response:{Colors.END}")
        if isinstance(response, dict):
            if "response" in response:
                resp_text = response["response"]
                if len(resp_text) > max_length:
                    print(f"  {resp_text[:max_length]}...\n  [Response truncated for readability]")
                else:
                    print(f"  {resp_text}")
            else:
                print(f"  {json.dumps(response, indent=2)}")
        else:
            print(f"  {response}")
    
    def check_backend(self) -> bool:
        """Check if backend is running"""
        self.print_section("Checking backend connectivity...")
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=20)
            if response.status_code == 200:
                self.print_success(f"Backend is running at {self.backend_url}")
                return True
            else:
                self.print_error(f"Backend returned status code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error(f"Cannot connect to backend at {self.backend_url}")
            self.print_info("Make sure to run: uvicorn app.main:app --reload")
            return False
        except Exception as e:
            self.print_error(f"Error checking backend: {str(e)}")
            return False
    
    def scenario_1_greeting(self):
        """Scenario 1: Patient Greeting & Discharge Report Retrieval"""
        self.print_header("SCENARIO 1: Patient Greeting & Discharge Report Retrieval")
        
        scenario_name = "Patient Greeting"
        try:
            patient_name = "John Smith"
            self.print_section(f"Greeting patient: {patient_name}")
            self.print_info(f"Diagnosis: Chronic Kidney Disease Stage 3")
            
            # Make API call
            response = requests.post(
                f"{self.backend_url}/api/greet",
                json={"patient_name": patient_name},
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                self.print_success(f"Session created: {data.get('session_id')}")
                
                # Store session for later use
                self.sessions[patient_name] = data.get("session_id")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED",
                    "session_id": data.get("session_id")
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_2_medical_query(self):
        """Scenario 2: Medical Query with Agent Handoff"""
        self.print_header("SCENARIO 2: Medical Query with Agent Handoff")
        
        scenario_name = "Medical Query Routing"
        try:
            patient_name = "John Smith"
            
            if patient_name not in self.sessions:
                self.print_error("No active session for this patient. Run Scenario 1 first.")
                self.demo_results["failed"] += 1
                self.demo_results["total_scenarios"] += 1
                return
            
            session_id = self.sessions[patient_name]
            query = "I'm having swelling in my legs and feel very tired. Is this normal?"
            
            self.print_section(f"Patient query: {query}")
            self.print_info("Expected: Route to Clinical Agent (medical concern detected)")
            
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={
                    "patient_name": patient_name,
                    "session_id": session_id,
                    "query": query
                },
                timeout=25
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_used = data.get("agent_used", "Unknown")
                self.print_info(f"Agent used: {agent_used}")
                self.print_response(data)
                
                if "Clinical" in agent_used:
                    self.print_success("Correctly routed to Clinical Agent")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED",
                    "agent_used": agent_used
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_3_research_query(self):
        """Scenario 3: Research Query with Web Search"""
        self.print_header("SCENARIO 3: Recent Research Query (Web Search)")
        
        scenario_name = "Web Search Fallback"
        try:
            patient_name = "Emily Rodriguez"
            
            self.print_section(f"Greeting patient: {patient_name}")
            self.print_info(f"Diagnosis: Diabetic Nephropathy Stage 3b")
            
            # First greet patient
            greet_response = requests.post(
                f"{self.backend_url}/api/greet",
                json={"patient_name": patient_name},
                timeout=20
            )
            
            if greet_response.status_code != 200:
                raise Exception("Failed to greet patient")
            
            session_id = greet_response.json().get("session_id")
            self.sessions[patient_name] = session_id
            self.print_success(f"Session created: {session_id}")
            
            time.sleep(1)
            
            # Now ask research question
            query = "I read about SGLT2 inhibitors for kidney disease. Can I use them? Are they effective?"
            self.print_section(f"Patient query: {query}")
            self.print_info("Expected: Web search for latest research on SGLT2 inhibitors")
            
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={
                    "patient_name": patient_name,
                    "session_id": session_id,
                    "query": query
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                
                if "SGLT2" in data.get("response", ""):
                    self.print_success("Web search successfully retrieved information")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED"
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_4_medications(self):
        """Scenario 4: Medication Information Lookup"""
        self.print_header("SCENARIO 4: Medication Information Lookup")
        
        scenario_name = "Medication Retrieval"
        try:
            patient_name = "Robert Williams"
            
            self.print_section(f"Greeting patient: {patient_name}")
            self.print_info(f"Diagnosis: CKD Stage 4 - Preparation for dialysis")
            
            # Greet patient
            greet_response = requests.post(
                f"{self.backend_url}/api/greet",
                json={"patient_name": patient_name},
                timeout=20
            )
            
            if greet_response.status_code != 200:
                raise Exception("Failed to greet patient")
            
            session_id = greet_response.json().get("session_id")
            self.sessions[patient_name] = session_id
            self.print_success(f"Session created: {session_id}")
            
            time.sleep(1)
            
            # Ask about medications
            query = "What medications am I taking and why? I'm confused about all these pills."
            self.print_section(f"Patient query: {query}")
            self.print_info("Expected: Receptionist Agent provides medication education")
            
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json={
                    "patient_name": patient_name,
                    "session_id": session_id,
                    "query": query
                },
                timeout=25
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_response(data)
                
                if "Calcitriol" in data.get("response", "") or "Sevelamer" in data.get("response", ""):
                    self.print_success("Medication information retrieved correctly")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED"
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_5_session_history(self):
        """Scenario 5: Multi-turn Conversation & Session History"""
        self.print_header("SCENARIO 5: Session History & Multi-Turn Conversation")
        
        scenario_name = "Session History"
        try:
            patient_name = "John Smith"
            
            if patient_name not in self.sessions:
                self.print_error("No active session for this patient")
                self.demo_results["failed"] += 1
                self.demo_results["total_scenarios"] += 1
                return
            
            session_id = self.sessions[patient_name]
            self.print_section(f"Retrieving conversation history for session: {session_id}")
            
            response = requests.get(
                f"{self.backend_url}/api/session/{session_id}",
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_info(f"Total interactions: {data.get('interactions_count', 0)}")
                
                if data.get("interactions"):
                    for i, interaction in enumerate(data["interactions"][:3], 1):
                        print(f"\n  Interaction {i}:")
                        print(f"    Agent: {interaction.get('agent')}")
                        print(f"    User: {interaction.get('user_input')[:50]}...")
                
                self.print_success("Session history retrieved successfully")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED",
                    "interaction_count": data.get("interactions_count", 0)
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_6_admin_monitoring(self):
        """Scenario 6: Admin Monitoring & System Logs"""
        self.print_header("SCENARIO 6: Admin Monitoring & System Logs")
        
        scenario_name = "Admin Monitoring"
        try:
            self.print_section("Listing all active sessions...")
            
            response = requests.post(
                f"{self.backend_url}/api/sessions/list",
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                total_sessions = data.get("total_sessions", 0)
                self.print_success(f"Total active sessions: {total_sessions}")
                
                if data.get("sessions"):
                    print("\n  Active Sessions:")
                    for session in data["sessions"][:5]:
                        print(f"    - {session.get('patient_name')}: {session.get('interaction_count')} interactions")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED",
                    "total_sessions": total_sessions
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def scenario_7_rag_stats(self):
        """Scenario 7: Vector Database Statistics"""
        self.print_header("SCENARIO 7: Vector Database Statistics")
        
        scenario_name = "RAG Statistics"
        try:
            self.print_section("Retrieving vector store statistics...")
            
            response = requests.get(
                f"{self.backend_url}/api/rag/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                print(f"\n{Colors.YELLOW}Vector Store Stats:{Colors.END}")
                print(f"  Total Documents: {stats.get('total_documents', 0)}")
                print(f"  Collections: {stats.get('collections', 0)}")
                
                self.print_success("RAG system is operational")
                
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "PASSED",
                    "total_documents": stats.get('total_documents', 0)
                })
                self.demo_results["passed"] += 1
            else:
                self.print_error(f"API returned status {response.status_code}")
                self.demo_results["scenarios"].append({
                    "scenario": scenario_name,
                    "status": "FAILED",
                    "error": response.text
                })
                self.demo_results["failed"] += 1
        
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            self.demo_results["scenarios"].append({
                "scenario": scenario_name,
                "status": "FAILED",
                "error": str(e)
            })
            self.demo_results["failed"] += 1
        
        self.demo_results["total_scenarios"] += 1
        time.sleep(DEMO_DELAY)
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("DEMO WORKFLOW SUMMARY")
        
        total = self.demo_results["total_scenarios"]
        passed = self.demo_results["passed"]
        failed = self.demo_results["failed"]
        
        print(f"Total Scenarios: {Colors.BOLD}{total}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{Colors.BOLD}{passed}{Colors.END}")
        print(f"Failed: {Colors.RED}{Colors.BOLD}{failed}{Colors.END}")
        
        if failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All scenarios passed!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠ Some scenarios failed. Check errors above.{Colors.END}")
        
        print(f"\n{Colors.CYAN}Detailed Results:{Colors.END}")
        for scenario in self.demo_results["scenarios"]:
            status = f"{Colors.GREEN}PASSED{Colors.END}" if scenario["status"] == "PASSED" else f"{Colors.RED}FAILED{Colors.END}"
            print(f"  {scenario['scenario']}: {status}")
        
        print(f"\n{Colors.BOLD}Timestamp: {datetime.now().isoformat()}{Colors.END}")
    
    def run_all_scenarios(self):
        """Run all demo scenarios"""
        self.print_header("MEDICAL AI POC - COMPLETE WORKFLOW DEMONSTRATION")
        print(f"{Colors.BOLD}Starting automated workflow demonstration...{Colors.END}\n")
        
        # Check backend first
        if not self.check_backend():
            self.print_error("Cannot proceed without backend. Exiting.")
            return False
        
        time.sleep(2)
        
        # Run scenarios
        self.scenario_1_greeting()
        self.scenario_2_medical_query()
        self.scenario_3_research_query()
        self.scenario_4_medications()
        self.scenario_5_session_history()
        self.scenario_6_admin_monitoring()
        self.scenario_7_rag_stats()
        
        # Print summary
        self.print_summary()
        
        return self.demo_results["failed"] == 0


def main():
    """Main entry point"""
    demo = DemoWorkflow()
    success = demo.run_all_scenarios()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
