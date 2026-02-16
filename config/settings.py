# config/settings.py
from __future__ import annotations
 
import os
from pathlib import Path
from dataclasses import dataclass
 
# ============================================================
# 1) PROJECT ROOT & STANDARD DIRECTORIES (Part-1 focused)
# ============================================================
# Repo root resolve (…/resume-parsing-system/)
REPO_ROOT: Path = Path(__file__).resolve().parents[1]
 
# Core folders (Part-1)
RESUMES_RAW_DIR: Path = REPO_ROOT / "resumes_raw"
RESUMES_TXT_DIR: Path = REPO_ROOT / "resumes_txt"
RESUME_JSON_DIR: Path = REPO_ROOT / "resume_json"
CACHE_DIR: Path = REPO_ROOT / "cache"
SCHEMA_DIR: Path = REPO_ROOT / "schema"
LOGS_DIR: Path = REPO_ROOT / "logs"
 
# Files
RESUME_SCHEMA_PATH: Path = SCHEMA_DIR / "resume_schema.json"
PARSER_LOG_PATH: Path = LOGS_DIR / "parser.log"
 
# Ensure directories exist (safe idempotent creation)
for d in (RESUMES_RAW_DIR, RESUMES_TXT_DIR, RESUME_JSON_DIR, CACHE_DIR, SCHEMA_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)
# Ensure log file exists so logging handlers don’t fail
if not PARSER_LOG_PATH.exists():
    PARSER_LOG_PATH.touch()
 
 
# ============================================================
# 2) ENVIRONMENT VARIABLES (.env → setx/export)
#    NEVER hard-code secrets in code.
# ============================================================
# Required:
#   GROQ_API_KEY      -> your Groq key
#   GROQ_MODEL_NAME   -> e.g., "llama-3.1-70b-versatile"
# Optional:
#   DEBUG_SETTINGS    -> "0" or "1"
 
GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
MODEL_NAME: str = os.environ.get("GROQ_MODEL_NAME", "llama-3.1-70b-versatile")
DEBUG_SETTINGS: str = os.environ.get("DEBUG_SETTINGS", "0")
 
# (We don't import dotenv to keep runtime simple & dependency-free.)
# On Windows (PowerShell):
#   setx GROQ_API_KEY "xxx"
#   setx GROQ_MODEL_NAME "llama-3.1-70b-versatile"
# On Mac/Linux (current shell):
#   export GROQ_API_KEY="xxx"
#   export GROQ_MODEL_NAME="llama-3.1-70b-versatile"
 
 
# ============================================================
# 3) LLM / GROQ CONFIGURATION (Parsing-friendly defaults)
# ============================================================
@dataclass(frozen=True)
class LLMConfig:
    provider: str = "groq"
    model_name: str = MODEL_NAME
    temperature: float = 0.0               # deterministic parsing
    max_output_tokens: int = 2048          # enough for large JSON
    request_timeout_sec: int = 60          # HTTP timeout per request
    max_retries: int = 3                   # retry on transient failures
    initial_backoff_sec: float = 1.0       # 1s → 2s → 4s
    backoff_multiplier: float = 2.0
    enforce_json_only: bool = True         # model must return JSON only
    min_seconds_between_calls: float = 0.25  # basic throttling
 
LLM = LLMConfig()
 
 
# ============================================================
# 4) PARSING / VALIDATION POLICY (Must align with your prompt)
# ============================================================
@dataclass(frozen=True)
class ParsePolicy:
    # Missing data policy (as per your strict instructions)
    missing_text: str = "insufficient data"  # for string fields
    missing_numeric_str: str = "0"           # numeric-in-string fields
    missing_list: tuple[str, ...] = tuple()  # for arrays
 
    # JSON discipline
    require_all_schema_fields: bool = True
    reject_additional_fields: bool = True
 
    # Experience computation
    compute_total_experience_from_items: bool = True
    # Expect total exp string in decimal like "5.7"
    total_exp_decimal_places: int = 1
 
POLICY = ParsePolicy()
 
 
# ============================================================
# 5) CACHING (hash-based to avoid repeat LLM calls)
# ============================================================
@dataclass(frozen=True)
class CacheConfig:
    enabled: bool = True
    dir: Path = CACHE_DIR
    # If you change parsing prompt materially, bump version to invalidate old cache
    cache_version: str = "v1"
 
CACHE = CacheConfig()
 
 
# ============================================================
# 6) LOGGING CONFIG (used by modules to configure handlers)
# ============================================================
@dataclass(frozen=True)
class LogConfig:
    log_file: Path = PARSER_LOG_PATH
    level: str = "INFO"  # "DEBUG" for verbose, else "INFO"
    fmt: str = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
 
LOG = LogConfig()
 
 
# ============================================================
# 7) UTILITIES
# ============================================================
def ensure_file(parent: Path, filename: str) -> Path:
    """Create empty file if not exists and return its path."""
    parent.mkdir(parents=True, exist_ok=True)
    p = parent / filename
    if not p.exists():
        p.touch()
    return p
 
 
# Optional debug prints (enable via DEBUG_SETTINGS=1)
if DEBUG_SETTINGS == "1":
    print("=== SETTINGS DEBUG ===")
    print(f"REPO_ROOT              : {REPO_ROOT}")
    print(f"RESUMES_RAW_DIR        : {RESUMES_RAW_DIR}")
    print(f"RESUMES_TXT_DIR        : {RESUMES_TXT_DIR}")
    print(f"RESUME_JSON_DIR        : {RESUME_JSON_DIR}")
    print(f"CACHE_DIR              : {CACHE_DIR}")
    print(f"SCHEMA_DIR             : {SCHEMA_DIR}")
    print(f"RESUME_SCHEMA_PATH     : {RESUME_SCHEMA_PATH}")
    print(f"LOG_FILE               : {PARSER_LOG_PATH}")
    print(f"GROQ_API_KEY set?      : {'yes' if GROQ_API_KEY else 'no'}")
    print(f"MODEL_NAME             : {MODEL_NAME}")
    print("======================")
 