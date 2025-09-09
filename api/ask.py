from http.server import BaseHTTPRequestHandler
import os, json
import openai

client = openai.OpenAI(
    api_key=os.getenv("POE_API_KEY"),
    base_url="https://api.poe.com/v1",
)

def _send(handler, status, data):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if not os.getenv("POE_API_KEY"):
            return _send(self, 500, {"error":"Missing POE_API_KEY"})
        try:
            length = int(self.headers.get("content-length", 0) or 0)
            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length>0 else {}
        except Exception:
            return _send(self, 400, {"error":"Invalid JSON body"})

        model = (payload.get("model") or os.getenv("POE_MODEL") or "claude-3-5-sonnet-20240620").strip()
        messages = payload.get("messages")
        if not messages:
            return _send(self, 400, {"error":"Missing messages"})

        try:
            chat = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=payload.get("temperature", 0.4),
                max_tokens=payload.get("max_tokens", 1024),
            )
            return _send(self, 200, chat.to_dict())
        except Exception as e:
            return _send(self, 500, {"error": str(e)})
