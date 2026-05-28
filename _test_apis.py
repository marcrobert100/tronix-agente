import requests

# Try Upsampler free API (they offer Wan 2.2)
urls = [
    "https://api.upsampler.com/generate",
    "https://upsampler.com/api/generate",
]
for url in urls:
    try:
        r = requests.post(url, json={"prompt": "dog surfing"}, timeout=15)
        print(f"{url}: {r.status_code}")
    except:
        print(f"{url}: failed")

# Try HuggingFace free inference
print("\n--- HF Inference ---")
r = requests.post(
    "https://api-inference.huggingface.co/models/THUDM/CogVideoX-5B",
    json={"inputs": "dog surfing"},
    timeout=30
)
print(f"CogVideoX: {r.status_code}")
