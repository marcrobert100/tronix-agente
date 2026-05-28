import requests
r = requests.get("http://localhost:8080/v1/toolkit/test", headers={"X-API-Key": "tronix_key_2026"}, timeout=10)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Message: {data.get('message', '')}")
print(f"Code: {data.get('code', '')}")
