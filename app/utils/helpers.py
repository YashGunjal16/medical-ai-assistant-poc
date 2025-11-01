import json
from pathlib import Path


def load_patient_data():
    """Load patient data from JSON file"""
    patient_file = Path("app/data/patients.json")
    with open(patient_file, "r") as f:
        return json.load(f)


def find_patient_by_name(patient_name: str):
    """Find patient in database by name"""
    patients = load_patient_data()
    
    # Case-insensitive search
    for patient in patients:
        if patient["patient_name"].lower() == patient_name.lower():
            return patient
    
    return None


def get_all_patients():
    """Get all patient names for reference"""
    patients = load_patient_data()
    return [p["patient_name"] for p in patients]


def format_patient_report(patient: dict) -> str:
    """Format patient data into readable discharge report"""
    report = f"""
--- DISCHARGE REPORT ---
Patient Name: {patient['patient_name']}
Patient ID: {patient['patient_id']}
Discharge Date: {patient['discharge_date']}
Age: {patient['age']} years

PRIMARY DIAGNOSIS:
{patient['primary_diagnosis']}

MEDICATIONS:
{chr(10).join(f"  • {med}" for med in patient['medications'])}

DIETARY RESTRICTIONS:
{patient['dietary_restrictions']}

FOLLOW-UP APPOINTMENTS:
{patient['follow_up']}

WARNING SIGNS TO WATCH:
{chr(10).join(f"  • {sign}" for sign in patient['warning_signs'].split(', '))}

DISCHARGE INSTRUCTIONS:
{patient['discharge_instructions']}
"""
    return report
