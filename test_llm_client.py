from modules.llm_client import call_llm
 
prompt = """
Return JSON:
{
    "name": "Test User",
    "role": "Developer"
}
"""
 
output = call_llm(prompt)
print(output)