from app.utils.helpers import find_patient_by_name, format_patient_report
from app.utils.logger import log_retrieval_attempt
from typing import Optional, Dict, Any


def retrieve_patient_data(patient_name: str) -> Optional[Dict[str, Any]]:
    """
    Dedicated tool for patient database retrieval
    Implements error handling and logging
    """
    try:
        log_retrieval_attempt("database", patient_name, False, "patient_db")
        
        patient = find_patient_by_name(patient_name)
        
        if patient:
            log_retrieval_attempt("database", patient_name, True, "patient_db")
            return {
                "success": True,
                "patient_data": patient,
                "formatted_report": format_patient_report(patient),
                "message": f"Found discharge report for {patient_name}"
            }
        else:
            log_retrieval_attempt("database", patient_name, False, "patient_db")
            return {
                "success": False,
                "patient_data": None,
                "message": f"No discharge report found for patient: {patient_name}",
                "error": "PATIENT_NOT_FOUND"
            }
    
    except Exception as e:
        log_retrieval_attempt("database", patient_name, False, "patient_db")
        return {
            "success": False,
            "patient_data": None,
            "message": f"Error retrieving patient data: {str(e)}",
            "error": "DATABASE_ERROR"
        }
