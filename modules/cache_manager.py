# modules/cache_manager.py
 
import hashlib
import json
from pathlib import Path
import logging
 
from config.settings import CACHE, LOG
from modules.file_manager import save_json_to, load_json_from
 
 
# -----------------------------------------------------------
# Logger setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("cache_manager")
 
 
# -----------------------------------------------------------
# 1) Generate MD5 hash of text content
# -----------------------------------------------------------
def generate_hash(text: str) -> str:
    """
    Generates an MD5 hash of resume TXT content.
    Hash is used as cache key.
    """
    try:
        hash_key = hashlib.md5(text.encode("utf-8")).hexdigest()
        versioned_key = f"{CACHE.cache_version}_{hash_key}"
        return versioned_key
 
    except Exception as e:
        logger.error(f"Error generating MD5 hash: {e}", exc_info=True)
        return None
 
 
# -----------------------------------------------------------
# 2) Build cache file path
# -----------------------------------------------------------
def get_cache_file_path(hash_key: str) -> Path:
    """
    Returns the full path of cache file based on hash.
    """
    return CACHE.dir / f"{hash_key}.json"
 
 
# -----------------------------------------------------------
# 3) Check if cache exists
# -----------------------------------------------------------
def cache_exists(hash_key: str) -> bool:
    """
    Returns True if cache file exists.
    """
    try:
        path = get_cache_file_path(hash_key)
        return path.exists()
    except Exception as e:
        logger.error(f"Error checking cache existence: {e}", exc_info=True)
        return False
 
 
# -----------------------------------------------------------
# 4) Load JSON from cache
# -----------------------------------------------------------
def load_cache(hash_key: str) -> dict:
    """
    Loads cached JSON for a given hash key.
    """
    try:
        path = get_cache_file_path(hash_key)
        if path.exists():
            logger.info(f"[CACHE HIT] Loading cache: {path}")
            return load_json_from(path)
 
        logger.info(f"[CACHE MISS] No cache for: {hash_key}")
        return {}
 
    except Exception as e:
        logger.error(f"Error loading cache: {e}", exc_info=True)
        return {}
 
 
# -----------------------------------------------------------
# 5) Save JSON to cache
# -----------------------------------------------------------
def save_cache(hash_key: str, data: dict) -> bool:
    """
    Saves parsed JSON to cache folder.
    """
    try:
        path = get_cache_file_path(hash_key)
        save_json_to(path, data)
        logger.info(f"[CACHE SAVED] {path}")
        return True
 
    except Exception as e:
        logger.error(f"Error saving cache: {e}", exc_info=True)
        return False
 