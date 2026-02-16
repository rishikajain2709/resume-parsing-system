# modules/resume_parser.py
 
from __future__ import annotations
 
import logging
from pathlib import Path
from typing import Dict, Any
 
from config.settings import (
    LOG,
    POLICY
)
 
from modules.file_manager import read_txt, write_json
from modules.converter import convert_to_txt
from modules.cache_manager import (
    generate_hash,
    cache_exists,
    load_cache,
    save_cache
)
from modules.llm_client import call_llm
from modules.schema_loader import (
    load_resume_schema,
    validate_resume_json
)
 
 
# -----------------------------------------------------------
# Logger Setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("resume_parser")
 
 
# -----------------------------------------------------------
# LOAD RESUME SCHEMA (ONCE)
# -----------------------------------------------------------
RESUME_SCHEMA = load_resume_schema()
 
 
# -----------------------------------------------------------
# BUILD LLM PROMPT
# -----------------------------------------------------------

def build_prompt(txt_content: str) -> str:
    """
    Strict schema-based prompt for resume-to-JSON transformation.
    """
    import json

    # Load global schema
    schema_text = json.dumps(RESUME_SCHEMA, indent=2)

    prompt = f"""
You are an expert resume-to-JSON converter.

You MUST generate JSON that EXACTLY matches the following schema:

==================== JSON SCHEMA ====================
{schema_text}
====================================================

MAPPING RULES:
---------------------------------------
- Candidate_name → Full name from resume
- Current_Role → Person's current job title
- Candidate_grade → If not found → "insufficient data"
- Profile_location → Extract city/state if possible
- Domains_known → Technologies, domains, areas of work
- Total_experience_years → extract years OR "insufficient data"

Tech_skillset.primary_tech_skills →
    Extract programming languages, frameworks, tools

Tech_skillset.secondary_tech_skills →
    Other optional technologies

Functional_skillset →
    Soft skills / functional capabilities

Overall_responsibilities →
    Duties extracted from projects/experience

Previously_worked_for_the_customer →
    ONLY "yes", "no", or "insufficient data"

Count_of_projects →
    Number of project blocks found

Current_project_age →
    Duration of latest project OR "insufficient data"

Fitness_summary →
    Achievements / recognitions (as array)

STRICT RULES:
------------------------
- Use EXACT field names from schema.
- Do NOT add new fields.
- Do NOT remove any field.
- Arrays must remain arrays.
- Missing string field → "insufficient data"
- Missing array → []
- Missing numeric string → "0"
- Output MUST BE ONLY VALID JSON (no explanation).

Now parse this resume:
=================== RESUME TEXT ======================
{txt_content}
======================================================

Return ONLY valid JSON.
"""

    return prompt.strip()


# def build_prompt(txt_content: str) -> str:
#     """
#     Creates the main parsing instruction prompt for Groq LLM.
#     Includes ALL strict rules & schema compliance instructions.
#     """
 
#     prompt = f"""
# You are a strict resume-to-JSON parser.
 
# Your task:
# - Extract structured information from the resume text.
# - Output MUST be valid JSON (no text outside JSON).
# - Follow ALL fields exactly as per schema.
# - Fill missing fields strictly using these rules:
#     * Missing string → "insufficient data"
#     * Missing array → []
#     * Missing numeric string → "0"
 
# Rules:
# - No hallucination.
# - No adding fields not in schema.
# - Total experience must be a SINGLE STRING number like "5.7".
# - Experiences list must be respected ONLY if resume contains it.
# - If any field cannot be detected → "insufficient data".
 
# Here is the resume text:
# --------------------------------
# {txt_content}
# --------------------------------
 
# Return ONLY valid JSON object.
#     """
 
#     return prompt.strip()
 
 
 
 
# -----------------------------------------------------------
# MAIN FUNCTION: Parse a single resume (PDF/DOCX/TXT)
# -----------------------------------------------------------
def parse_single_resume(raw_path: Path) -> Dict[str, Any]:
    """
    FULL PIPELINE:
    - Convert → TXT
    - Load TXT
    - Cache lookup
    - LLM call
    - JSON fix
    - Schema validation
    - Save output JSON
    """
 
    logger.info(f"[PARSER] Processing resume: {raw_path}")
 
    # STEP 1: Convert PDF/DOCX → TXT
    txt_path = convert_to_txt(raw_path)
    if not txt_path:
        logger.error(f"[PARSER] TXT conversion failed: {raw_path}")
        return {}
 
    # STEP 2: Read TXT file
    txt_content = read_txt(txt_path)
    if not txt_content.strip():
        logger.error(f"[PARSER] TXT empty after conversion: {txt_path}")
        return {}
 
    # STEP 3: Cache hashing
    hash_key = generate_hash(txt_content)
    if not hash_key:
        logger.error("[PARSER] Failed generating cache hash.")
        return {}
 
    # STEP 4: Cache HIT
    if cache_exists(hash_key):
        logger.info(f"[CACHE HIT] Using cached JSON for: {raw_path}")
        return load_cache(hash_key)
 
    # STEP 5: Build LLM prompt
    prompt = build_prompt(txt_content)
 
    # STEP 6: CALL LLM (safe)
    llm_output = call_llm(prompt)
    if not llm_output:
        logger.error("[PARSER] LLM returned empty output.")
        return {}
 
    # STEP 7: Validate + auto-fill fields as per schema
    is_valid, fixed_json, errors = validate_resume_json(
        llm_output,
        RESUME_SCHEMA,
        fill_missing=True,
        strip_extra=True
    )
 
    if not is_valid:
        logger.warning(f"[PARSER] Validation issues: {errors}")
 
    # STEP 8: Save to cache
    save_cache(hash_key, fixed_json)
 
    # STEP 9: Save final resume JSON
    output_file = raw_path.stem + ".json"
    write_json(output_file, fixed_json)
 
    logger.info(f"[PARSER] Successfully parsed & saved: {output_file}")
 
    return fixed_json
 
 
# -----------------------------------------------------------
# PUBLIC API: Parse Entire Folder (resumes_raw/)
# -----------------------------------------------------------
def parse_all_resumes(raw_folder: Path) -> None:
    """
    Iterate through all resumes in folder and parse each.
    """
 
    logger.info("[PARSER] Starting bulk resume parsing...")
 
    for file in raw_folder.iterdir():
        if file.suffix.lower() in [".pdf", ".docx", ".txt"]:
            parse_single_resume(file)
 
    logger.info("[PARSER] Bulk parsing completed.")