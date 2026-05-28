import os
import sys
import json
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.join(os.path.dirname(__file__), "nca_storage")
os.makedirs(ROOT, exist_ok=True)

class S3Handler(BaseHTTPRequestHandler):
    def _send(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if body:
            self.wfile.write(body if isinstance(body, bytes) else json.dumps(body).encode())

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        key = path.split("/")[-1]
        dest = os.path.join(ROOT, key)
        with open(dest, "wb") as f:
            f.write(body)
        public_url = f"http://localhost:9090/{key}"
        self._send(200, {"url": public_url})

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        key = path.lstrip("/")
        filepath = os.path.join(ROOT, key)
        if os.path.exists(filepath):
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            with open(filepath, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._send(404, {"error": "not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.end_headers()

if __name__ == "__main__":
    port = 9090
    server = HTTPServer(("0.0.0.0", port), S3Handler)
    print(f"LocalS3 rodando em http://localhost:{port}")
    print(f"Storage: {ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
