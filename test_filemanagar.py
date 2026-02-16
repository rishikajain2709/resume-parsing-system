from modules.file_manager import (
    list_raw_resumes,
    write_txt,
    read_txt,
    write_json,
    read_json
)
 
def test_all():
    print("=== TEST START ===")
 
    # 1. Test list_raw_resumes (should be empty initially)
    print("Raw resumes:", list_raw_resumes())
 
    # 2. Test TXT write & read
    txt_path = write_txt("sample_test.txt", "This is test content")
    print("TXT written at:", txt_path)
 
    print("TXT read content:", read_txt(txt_path))
 
    # 3. Test JSON write & read
    json_path = write_json("sample_test.json", {"name": "Ujval", "role": "Engineer"})
    print("JSON written at:", json_path)
 
    print("JSON read content:", read_json(json_path))
 
    print("=== TEST COMPLETE ===")
 
 
if __name__ == "__main__":
    test_all()