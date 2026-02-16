from pathlib import Path
from modules.resume_parser import parse_single_resume
 
raw_file = Path("resumes_raw\\SIDDHARTH_RESUME_CAPGEMINI.docx")
json_output = parse_single_resume(raw_file)
 
print(json_output)