from modules.converter import convert_to_txt
from modules.file_manager import list_raw_resumes
 
resumes = list_raw_resumes()
for file in resumes:
    print("Converting:", file)
    out = convert_to_txt(file)
    print("Output:", out)