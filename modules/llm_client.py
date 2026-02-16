# modules/llm_client.py
 
import time
import logging
import json
import requests
 
from typing import Dict, Any, Tuple
 
from config.settings import (
    GROQ_API_KEY,
    LLM,
    LOG
)
from modules.json_fix import fix_json
 
 
# -----------------------------------------------------------
# Logger Setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("llm_client")
 
 
# -----------------------------------------------------------
# Build Groq API Request Payload
# -----------------------------------------------------------
def _build_payload(prompt: str) -> Dict[str, Any]:
    """
    Creates Groq API payload with strict JSON-only response enforced.
    """
    return {
        "model": LLM.model_name,
        "messages": [
            {"role": "system", "content": "You must reply ONLY with valid JSON. No explanations."},
            {"role": "user", "content": prompt}
        ],
        "temperature": LLM.temperature,
        "max_tokens": LLM.max_output_tokens
    }
 
 
# -----------------------------------------------------------
# Make Request to Groq API
# -----------------------------------------------------------
def _call_groq_api(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Raw API call to Groq.
    Returns (success, raw_output)
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
 
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
 
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=LLM.request_timeout_sec
        )
 
        if response.status_code != 200:
            logger.error(f"Groq API Returned {response.status_code}: {response.text}")
            return False, ""
 
        content = response.json()["choices"][0]["message"]["content"]
        return True, content
 
    except requests.exceptions.Timeout:
        logger.error("Groq API Timeout")
        return False, ""
 
    except requests.exceptions.ConnectionError:
        logger.error("Groq API Connection Error")
        return False, ""
 
    except Exception as e:
        logger.error(f"Groq API Unexpected Error: {e}", exc_info=True)
        return False, ""
 
 
# -----------------------------------------------------------
# Public Function — Safe LLM Call
# -----------------------------------------------------------
def call_llm(prompt: str) -> Dict[str, Any]:
    """
    Calls Groq API safely with:
    - Retries
    - Backoff
    - Hard JSON enforcement
    - JSON repair fallback
    """
 
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is missing. Set it in your environment.")
 
    payload = _build_payload(prompt)
    retries = LLM.max_retries
    backoff = LLM.initial_backoff_sec
 
    for attempt in range(1, retries + 1):
 
        logger.info(f"[LLM] Attempt {attempt}/{retries}")
 
        success, raw_output = _call_groq_api(payload)
 
        if success and raw_output.strip():
            # STEP 1: Try repairing JSON
            fixed_json = fix_json(raw_output)
 
            # STEP 2: Ensure dict
            if isinstance(fixed_json, dict):
                logger.info("[LLM] JSON successfully fixed & returned.")
                return fixed_json
            else:
                logger.warning("[LLM] JSON fix returned invalid structure.")
 
        # If failed, backoff
        logger.warning(f"[LLM] Retry in {backoff}s ...")
        time.sleep(backoff)
        backoff *= LLM.backoff_multiplier
 
    # FINAL: All retries failed
    logger.error("[LLM] All retries failed. Returning empty JSON.")
    return {}