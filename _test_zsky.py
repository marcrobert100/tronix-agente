import requests

urls = [
    "https://zsky.ai/api/v1/video/generate",
    "https://www.zsky.ai/api/v1/video/generate",
]
for url in urls:
    try:
        r = requests.post(url, json={"prompt": "dog surfing", "duration": 3}, timeout=30)
        print(f"{url}: {r.status_code}")
        print(f"  {r.text[:200]}")
    except Exception as e:
        print(f"{url}: error - {e}")
