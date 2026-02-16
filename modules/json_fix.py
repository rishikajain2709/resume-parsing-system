# modules/json_fix.py
 
import json
import logging
import re
from typing import Any, Dict, Tuple
 
from config.settings import LOG
 
# -----------------------------------------------------------
# Logger Setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("json_fix")
 
 
# -----------------------------------------------------------
# 1) Extract JSON object from messy LLM output
# -----------------------------------------------------------
def extract_json_text(raw_text: str) -> str:
    """
    Extracts JSON block from LLM output.
    Finds the first '{' and last '}' and extracts substring.
    Safely removes markdown, text, or commentary around JSON.
    """
 
    if raw_text is None:
        return ""
 
    # Remove Markdown fencing if present
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
 
    # Find first '{' and last '}'
    start = raw_text.find("{")
    end = raw_text.rfind("}")
 
    if start == -1 or end == -1:
        logger.warning("JSON braces not found in LLM output.")
        return raw_text
 
    return raw_text[start:end + 1]
 
 
# -----------------------------------------------------------
# 2) Try to directly load JSON
# -----------------------------------------------------------
def try_load_json(text: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        data = json.loads(text)
        return True, data
    except Exception:
        return False, {}
 
 
# -----------------------------------------------------------
# 3) Fix common JSON issues (quotes, commas, trailing chars)
# -----------------------------------------------------------
def apply_common_fixes(text: str) -> str:
    """
    Fixes:
    - Single quotes → double quotes
    - Remove trailing commas
    - Fix key:value JSON format issues
    - Remove repeated spaces, weird characters
    """
 
    fixed = text
 
    # Replace single quotes with double quotes safely
    fixed = fixed.replace("'", '"')
 
    # Remove trailing commas before }
    fixed = re.sub(r",\s*}", "}", fixed)
 
    # Remove trailing commas before ]
    fixed = re.sub(r",\s*]", "]", fixed)
 
    # Remove invalid control characters
    fixed = re.sub(r"[\x00-\x1F\x7F]", "", fixed)
 
    return fixed
 
 
# -----------------------------------------------------------
# 4) Hard Repair Mechanism (guaranteed fallback)
# -----------------------------------------------------------
def hard_json_repair(text: str) -> Dict[str, Any]:
    """
    Last resort repair strategy.
    Attempts to rebuild JSON structure field-by-field.
    Only used if all other parsing fails.
    """
 
    logger.warning("Hard JSON repair initiated...")
 
    # Extract all "key": "value" patterns
    pattern = r'"(.*?)"\s*:\s*"(.*?)"'
    matches = re.findall(pattern, text)
 
    data = {}
    for key, value in matches:
        data[key] = value
 
    return data
 
 
# -----------------------------------------------------------
# 5) Main JSON fix function (called by llm_client)
# -----------------------------------------------------------
def fix_json(raw_text: str) -> Dict[str, Any]:
    """
    Full JSON correction pipeline:
    1) Extract JSON body
    2) Try direct load
    3) Apply common fixes
    4) Retry load
    5) Hard repair fallback
    """
 
    if raw_text is None or raw_text.strip() == "":
        logger.error("Raw LLM text is empty.")
        return {}
 
    # STEP 1 — Extract JSON block
    extracted = extract_json_text(raw_text)
 
    # STEP 2 — Try direct parse
    ok, data = try_load_json(extracted)
    if ok:
        return data
 
    # STEP 3 — Apply common repair fixes
    repaired = apply_common_fixes(extracted)
 
    # STEP 4 — Retry JSON load
    ok, data = try_load_json(repaired)
    if ok:
        return data
 
    # STEP 5 — Hard fallback repair
    hard_fixed = hard_json_repair(repaired)
 
    logger.warning("JSON fixed using fallback mode.")
    return hard_fixed
 