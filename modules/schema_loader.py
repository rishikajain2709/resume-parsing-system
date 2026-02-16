# modules/schema_loader.py
 
from __future__ import annotations
 
import json
import logging
from pathlib import Path
from typing import Any, Dict, Tuple, List
 
from config.settings import (
    RESUME_SCHEMA_PATH,
    POLICY,
    LOG
)
 
# Optional: Use jsonschema if present; otherwise fallback validator will be used
try:
    import jsonschema  # type: ignore
    HAS_JSONSCHEMA = True
except Exception:
    HAS_JSONSCHEMA = False
 
 
# -----------------------------------------------------------
# Logger setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("schema_loader")
 
 
# -----------------------------------------------------------
# 1) Load schema from file
# -----------------------------------------------------------
def load_resume_schema(path: Path = RESUME_SCHEMA_PATH) -> Dict[str, Any]:
    """
    Loads the resume JSON schema from disk.
    Raises FileNotFoundError if not present.
    """
    if not path.exists():
        msg = f"Resume schema not found at: {path}"
        logger.error(msg)
        raise FileNotFoundError(msg)
 
    try:
        with open(path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        logger.info(f"Loaded resume schema from: {path}")
        return schema
 
    except Exception as e:
        logger.error(f"Failed to load schema: {e}", exc_info=True)
        raise
 
 
# -----------------------------------------------------------
# 2) Policy-based filler for missing fields
#    (Ensures every field defined in schema exists in output)
# -----------------------------------------------------------
def _default_value_for_schema(schema_fragment: Dict[str, Any]) -> Any:
    """
    Return default based on schema type and project policy.
    """
    t = schema_fragment.get("type")
    if t == "string":
        return POLICY.missing_text
    if t == "array":
        return list(POLICY.missing_list)  # default empty list
    if t == "object":
        return {}
    # For anything numeric wrapped as string in your schema (e.g., "Total_experience_years")
    # the schema says "type": "string", so above branch handles it.
    return None
 
 
def fill_missing_fields(instance: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively ensure that all keys present in schema are present in instance.
    Apply project policy defaults for missing fields.
    """
    if not isinstance(instance, dict):
        return {}
 
    props = schema.get("properties", {})
    out = dict(instance)  # shallow copy
 
    for key, sub_schema in props.items():
        if key not in out:
            out[key] = _default_value_for_schema(sub_schema)
 
        # Recurse for nested structures
        sub_type = sub_schema.get("type")
        if sub_type == "object" and isinstance(out.get(key), dict):
            out[key] = fill_missing_fields(out[key], sub_schema)
        elif sub_type == "array":
            # If array of objects, we don't hallucinate items; we only ensure array presence.
            # If the array exists and contains objects with their own schema (items.type == object),
            # you could iterate and normalize each item here if you define a nested schema.
            pass
 
    return out
 
 
# -----------------------------------------------------------
# 3) Remove additional properties (if disallowed in schema)
# -----------------------------------------------------------
def strip_additional_properties(instance: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    If schema has "additionalProperties": False, remove keys not in schema.properties.
    Applies recursively to nested objects.
    """
    if not isinstance(instance, dict):
        return instance
 
    additional_allowed = schema.get("additionalProperties", True)
    props = schema.get("properties", {})
    out = {}
 
    for key, val in instance.items():
        if key in props:
            sub_schema = props[key]
            if isinstance(val, dict) and sub_schema.get("type") == "object":
                out[key] = strip_additional_properties(val, sub_schema)
            else:
                out[key] = val
        else:
            if additional_allowed:
                out[key] = val
            else:
                # drop this key
                logger.debug(f"Stripping additional property: {key}")
 
    return out
 
 
# -----------------------------------------------------------
# 4) Lightweight fallback validation (if jsonschema missing)
# -----------------------------------------------------------
def _fallback_basic_validate(instance: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Minimal validation when jsonschema is not available:
    - checks 'required' keys exist
    - checks basic 'type' compliance for strings/arrays/objects
    - warns on additionalProperties=False violations
    Returns list of error messages (empty => valid).
    """
    errors: List[str] = []
 
    if not isinstance(instance, dict):
        return ["Root must be an object"]
 
    props = schema.get("properties", {})
    required = schema.get("required", [])
    additional_allowed = schema.get("additionalProperties", True)
 
    # Required fields
    for r in required:
        if r not in instance:
            errors.append(f"Missing required field: {r}")
 
    # Type checks (basic)
    type_map = {
        "string": str,
        "object": dict,
        "array": list
    }
 
    for key, val in instance.items():
        if key in props:
            expected_type = props[key].get("type")
            if expected_type in type_map:
                py_type = type_map[expected_type]
                if not isinstance(val, py_type):
                    errors.append(f"Type mismatch for '{key}': expected {expected_type}, got {type(val).__name__}")
        else:
            if not additional_allowed:
                errors.append(f"Additional property not allowed: {key}")
 
    return errors
 
 
# -----------------------------------------------------------
# 5) Public API: validate with schema (and optionally fix)
# -----------------------------------------------------------
def validate_resume_json(
    instance: Dict[str, Any],
    schema: Dict[str, Any],
    *,
    fill_missing: bool = True,
    strip_extra: bool = True,
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate a resume JSON instance against schema.
    - Optionally fills missing fields based on POLICY defaults.
    - Optionally strips additional properties if schema forbids.
    Returns (is_valid, fixed_instance, errors)
    """
    fixed = dict(instance)
 
    # First, optionally strip extras (based on project policy)
    if strip_extra:
        fixed = strip_additional_properties(fixed, schema)
 
    # Optionally fill missing keys using policy
    if fill_missing:
        fixed = fill_missing_fields(fixed, schema)
 
    # Validate using jsonschema if available; else fallback
    errors: List[str] = []
 
    if HAS_JSONSCHEMA:
        try:
            jsonschema.validate(instance=fixed, schema=schema)  # type: ignore
        except Exception as e:
            # Collect detailed errors if available
            if hasattr(e, "message"):
                errors.append(getattr(e, "message"))
            else:
                errors.append(str(e))
    else:
        errors.extend(_fallback_basic_validate(fixed, schema))
 
    is_valid = len(errors) == 0
    if is_valid:
        logger.info("Resume JSON validated successfully against schema.")
    else:
        logger.warning(f"Resume JSON validation failed: {errors}")
 
    return is_valid, fixed, errors
 