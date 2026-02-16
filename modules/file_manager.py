# modules/file_manager.p
import os
import json
from pathlib import Path
from typing import List, Any, Dict
import logging
 
from config.settings import (
    RESUMES_RAW_DIR,
    RESUMES_TXT_DIR,
    RESUME_JSON_DIR,
    LOG
)
 
# Configure logger
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("file_manager")
 
 
# ============================================================
# 1) LIST RAW RESUME FILES (PDF / DOCX / DOC)
# ============================================================
 
def list_raw_resumes() -> List[Path]:
    """
    Returns list of resume files from resumes_raw/ directory.
    Allowed formats: .pdf, .docx, .doc
    """
    try:
        allowed_ext = [".pdf", ".docx", ".doc"]
        resumes = [
            f for f in RESUMES_RAW_DIR.iterdir()
            if f.suffix.lower() in allowed_ext and f.is_file()
        ]
        logger.info(f"Found {len(resumes)} raw resumes.")
        return resumes
 
    except Exception as e:
        logger.error(f"Error listing raw resumes: {e}", exc_info=True)
        return []
 
 
# ============================================================
# 2) READ TXT FILE
# ============================================================
 
def read_txt(path: Path) -> str:
    """
    Reads text content from a .txt file.
    """
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
 
    except Exception as e:
        logger.error(f"Error reading TXT file {path}: {e}", exc_info=True)
        return ""
 
 
# ============================================================
# 3) WRITE TXT FILE
# ============================================================
 
def write_txt(filename: str, content: str) -> Path:
    """
    Writes text content to a .txt file inside resumes_txt/ directory.
    Returns the output file path.
    """
    try:
        out_path = RESUMES_TXT_DIR / filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
 
        logger.info(f"TXT written: {out_path}")
        return out_path
 
    except Exception as e:
        logger.error(f"Error writing TXT file {filename}: {e}", exc_info=True)
        return None
 
 
# ============================================================
# 4) READ JSON (Resume JSON or Cache JSON)
# ============================================================
 
def read_json(path: Path) -> Dict[str, Any]:
    """
    Reads JSON file safely.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
 
    except Exception as e:
        logger.error(f"Error reading JSON file {path}: {e}", exc_info=True)
        return {}
 
 
# ============================================================
# 5) WRITE JSON (Resume JSON or Cache JSON)
# ============================================================
 
def write_json(filename: str, data: Dict[str, Any]) -> Path:
    """
    Writes JSON data to resume_json/ directory.
    Returns the file path.
    """
    try:
        out_path = RESUME_JSON_DIR / filename
 
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
 
        logger.info(f"JSON written: {out_path}")
        return out_path
 
    except Exception as e:
        logger.error(f"Error writing JSON file {filename}: {e}", exc_info=True)
        return None
 
 
# ============================================================
# 6) GENERIC SAVE JSON (custom folder)
# ============================================================
 
def save_json_to(path: Path, data: Dict[str, Any]) -> bool:
    """
    Save JSON to a custom path (used for cache).
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
 
        logger.info(f"Saved JSON to {path}")
        return True
 
    except Exception as e:
        logger.error(f"Error saving JSON to {path}: {e}", exc_info=True)
        return False
 
 
# ============================================================
# 7) READ CUSTOM JSON (cache or other)
# ============================================================
 
def load_json_from(path: Path) -> dict:
    """
    Generic JSON loader for any folder path.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
 
    except Exception as e:
        logger.error(f"Error loading JSON from {path}: {e}", exc_info=True)
        return {}