from modules.json_fix import fix_json
 
broken = """
Here is your output:
{
    'name': 'Ujval',
    'role': 'ETL Developer',
}
Thanks!
"""
 
fixed = fix_json(broken)
print(fixed)