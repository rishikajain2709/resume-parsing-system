from modules.cache_manager import generate_hash, save_cache, load_cache, cache_exists
 
text = "This is a sample resume content"
hash_key = generate_hash(text)
 
print("Hash Key:", hash_key)
print("Cache Exists (before):", cache_exists(hash_key))
 
data = {"name": "Ujval", "role": "Engineer"}
save_cache(hash_key, data)
 
print("Cache Exists (after):", cache_exists(hash_key))
print("Loaded:", load_cache(hash_key))
 