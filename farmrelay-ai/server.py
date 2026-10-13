"""FarmRelay AI: zero-dependency local demo server."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
sys.path.insert(0, str(ROOT))
from planner import build_plan


class FarmRelayHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:8000")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(200, {"ok": True, "service": "FarmRelay AI", "mode": "local-demo"})
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/plan":
            return self._json(404, {"error": "Route not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 100_000:
                return self._json(400, {"error": "Request body is missing or too large."})
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            result = build_plan(data)
            return self._json(200, result)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._json(400, {"error": "Please send valid JSON."})
        except ValueError as exc:
            return self._json(422, {"error": str(exc)})
        except Exception:
            return self._json(500, {"error": "Unexpected server error. Check the terminal logs."})


if __name__ == "__main__":
    host = os.environ.get("FARMRELAY_HOST", "127.0.0.1")
    port = int(os.environ.get("FARMRELAY_PORT", "8000"))
    print(f"FarmRelay AI running at http://{host}:{port}")
    print("Local demo only. Press Ctrl+C to stop.")
    ThreadingHTTPServer((host, port), FarmRelayHandler).serve_forever()
