import requests, json

r = requests.post("http://localhost:8080/v1/image/convert/video",
    headers={"X-API-Key": "tronix_key_2026", "Content-Type": "application/json"},
    json={"image_url": "C:/xampp/htdocs/agente/uploads/praia_1778570271.png", "duration": 6, "zoom": 1.08},
    timeout=120)

print(f"Status: {r.status_code}")
try:
    d = r.json()
    print(f"Code: {d.get('code','')}")
    msg = str(d.get("message",""))[:200]
    print(f"Message: {msg}")
    resp = str(d.get("response",""))[:300]
    print(f"Response: {resp}")
except:
    print(f"Raw: {r.text[:500]}")
