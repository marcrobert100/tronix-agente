import requests, json

base = "http://localhost:8080"
headers = {"X-API-Key": "tronix_key_2026", "Content-Type": "application/json"}

# Test 1: Toolkit test
print("=== 1. Test ===")
r = requests.get(f"{base}/v1/toolkit/test", headers=headers, timeout=10)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Message: {d.get('message','')}")
print(f"Code: {d.get('code','')}")

# Test 2: Image to video
print("\n=== 2. Image to Video ===")
img = "C:/xampp/htdocs/agente/uploads/cachorro_surf_1778565418.png"
r = requests.post(f"{base}/v1/image/convert/video", headers=headers,
    json={"image_url": img, "duration": 5, "zoom": 1.05}, timeout=120)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Code: {d.get('code','')}")
print(f"Response: {d.get('response','')}")
print(f"Message: {d.get('message','')}")
