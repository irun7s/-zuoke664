from http.server import BaseHTTPRequestHandler
import os, json, urllib.request, urllib.error

POE_URL = "https://api.poe.com/v1/chat/completions"

SYSTEM_PROMPT = (
    "用中文回答，直接给结论和步骤。"
    "禁止自我介绍、禁止复述身份或原则。"
    "如果信息不足，先用1句提问澄清。"
)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def _send(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        # 明确提示只允许 POST，便于 /api/ask 的自检
        return self._send(405, {"error": "Only POST allowed"})

    def do_POST(self):
        api_key = os.environ.get("POE_API_KEY")
        if not api_key:
            return self._send(500, {"error": "Missing POE_API_KEY"})

        try:
            length = int(self.headers.get("content-length", 0) or 0)
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "Invalid JSON body"})

        # 允许两种形态：直接 messages，或 text + imageDataUrl
        messages = payload.get("messages")
        text = (payload.get("text") or "").strip()
        image_data_url = payload.get("imageDataUrl")

        if not messages:
            if not text and not image_data_url:
                return self._send(400, {"error": "缺少文本或图片"})
            if image_data_url:
                parts = []
                if text:
                    parts.append({"type": "text", "text": text})
                parts.append({"type": "image_url", "image_url": {"url": image_data_url}})
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": parts},
                ]
            else:
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ]

        req_body = {
            "messages": messages,
            "temperature": 0.4
        }

        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(POE_URL, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_data = resp.read().decode("utf-8")
                obj = json.loads(resp_data)
                return self._send(resp.getcode(), obj)
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8") if e.fp else ""
            try:
                obj = json.loads(msg) if msg else {"error": e.reason}
            except Exception:
                obj = {"error": msg or e.reason}
            return self._send(e.code, obj)
        except Exception as e:
            return self._send(500, {"error": str(e)})

