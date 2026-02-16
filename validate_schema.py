# validate_schema.py
 
import json
from pathlib import Path
 
SCHEMA_PATH = Path("schema/resume_schema.json")
 
def check_json_format():
    """Check if resume_schema.json is valid JSON."""
    if not SCHEMA_PATH.exists():
        return False, "❌ ERROR: schema/resume_schema.json file not found!"
 
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        return True, schema
    except json.JSONDecodeError as e:
        return False, f"❌ JSON Format Error at line {e.lineno}, column {e.colno}:\n{e.msg}"
    except Exception as e:
        return False, f"❌ Unexpected Error: {str(e)}"
 
def check_required_fields(schema):
    """Check if schema contains required top-level structure."""
    required_keys = ["type", "properties"]
    missing = [key for key in required_keys if key not in schema]
 
    if missing:
        return False, f"❌ Missing required schema fields: {missing}"
 
    if schema.get("type") != "object":
        return False, "❌ Root 'type' must be 'object'."
 
    if not isinstance(schema.get("properties"), dict):
        return False, "❌ 'properties' must be a JSON object."
 
    return True, "OK"
 
def validate_schema():
    print("\n🔍 VALIDATING resume_schema.json ...\n")
 
    # Step 1 — JSON format check
    ok, result = check_json_format()
    if not ok:
        print(result)
        return
    else:
        print("✔ JSON is valid format.")
 
    schema = result
 
    # Step 2 — Required structural fields
    ok, result = check_required_fields(schema)
    if not ok:
        print(result)
        return
    else:
        print("✔ Basic structure valid.")
 
    # Step 3 — Optional detailed validation
    if "required" in schema:
        if not isinstance(schema["required"], list):
            print("❌ 'required' must be a list.")
            return
        print("✔ 'required' field is valid.")
 
    if "additionalProperties" in schema:
        if not isinstance(schema["additionalProperties"], bool):
            print("❌ 'additionalProperties' must be boolean.")
            return
        print("✔ 'additionalProperties' field is valid.")
 
    print("\n🎉 Schema validation SUCCESSFUL — Your schema is perfectly valid!\n")
 
if __name__ == "__main__":
    validate_schema()
 