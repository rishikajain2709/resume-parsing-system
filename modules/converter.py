# modules/converter.py
 
import logging
from pathlib import Path
 
import docx2txt
from PyPDF2 import PdfReader
 
from config.settings import (
    RESUMES_TXT_DIR,
    LOG
)
from modules.file_manager import write_txt
 
 
# -----------------------------------------------------------
# Logger setup
# -----------------------------------------------------------
logging.basicConfig(
    filename=LOG.log_file,
    level=LOG.level,
    format=LOG.fmt,
    datefmt=LOG.datefmt
)
logger = logging.getLogger("converter")
 
 
# -----------------------------------------------------------
# UTIL: clean extracted text
# -----------------------------------------------------------
def _clean_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\x00", "").strip()
 
 
# -----------------------------------------------------------
# 1) DOCX → TXT (docx2txt)
# -----------------------------------------------------------
def convert_docx_to_txt(path: Path) -> str:
    try:
        logger.info(f"[DOCX] Converting: {path}")
        text = docx2txt.process(str(path))
        return _clean_text(text)
 
    except Exception as e:
        logger.error(f"[DOCX] Conversion failed for {path}: {e}", exc_info=True)
        return ""
 
 
# -----------------------------------------------------------
# 2) PDF → TXT (PyPDF2 — Windows-safe)
# -----------------------------------------------------------
def convert_pdf_to_txt(path: Path) -> str:
    try:
        logger.info(f"[PDF] Converting: {path}")
 
        reader = PdfReader(str(path))
        text = ""
 
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
 
        return _clean_text(text)
 
    except Exception as e:
        logger.error(f"[PDF] Conversion failed for {path}: {e}", exc_info=True)
        return ""
 
 
# -----------------------------------------------------------
# 3) MAIN AUTO-DETECT CONVERTER
# -----------------------------------------------------------
def convert_to_txt(path: Path) -> Path | None:
    """
    Auto-detects file format and converts it to TXT.
    Supported: PDF, DOCX
    Ignored: DOC
    """
 
    ext = path.suffix.lower()
 
    # DOCX
    if ext == ".docx":
        text = convert_docx_to_txt(path)
 
    # PDF
    elif ext == ".pdf":
        text = convert_pdf_to_txt(path)
 
    # DOC => IGNORE (requested by you)
    elif ext == ".doc":
        logger.warning(f"[IGNORE] .doc file ignored: {path}")
        return None
 
    # Unsupported format
    else:
        logger.error(f"[ERROR] Unsupported format: {path}")
        return None
 
    # If empty text extracted
    if not text.strip():
        logger.error(f"[ERROR] No text extracted from {path}")
        return None
 
    # Save as .txt
    output_name = path.stem + ".txt"
    txt_path = write_txt(output_name, text)
 
    logger.info(f"[SUCCESS] Converted → {txt_path}")
    return txt_path