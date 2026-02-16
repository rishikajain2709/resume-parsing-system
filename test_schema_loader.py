from modules.schema_loader import load_resume_schema, validate_resume_json
import json
 
def main():
    schema = load_resume_schema()
 
    # A deliberately incomplete instance (missing many fields)
    instance = {
        "Candidate_name": "Ujval Rai",
        "Current_Role": "ETL Developer",
        "Tech_skillset": {
            "primary_tech_skills": ["Talend"],
            "secondary_tech_skills": ["SQL"]
        }
    }
 
    is_valid, fixed, errors = validate_resume_json(instance, schema)
 
    print("VALID:", is_valid)
    print("ERRORS:", errors)
    print("FIXED JSON:")
    print(json.dumps(fixed, indent=2))
 
if __name__ == "__main__":
    main()
 