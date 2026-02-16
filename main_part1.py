# main_part1.py
from pathlib import Path
from modules.resume_parser import parse_all_resumes
 
if __name__ == "__main__":
    raw_folder = Path("resumes_raw")  # no backslashes, platform-safe
    parse_all_resumes(raw_folder)
    print("✅ Done. Check 'resume_json/' for outputs and 'logs/parser.log' for details.")
 