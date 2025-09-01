from http.server import BaseHTTPRequestHandler
import os, json, urllib.request, urllib.error

POE_URL = "https://api.poe.com/v1/chat/completions"

class handler(BaseHTTPRequestHandler):
    # 允许跨域（前端不在同域时有用）
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

    def do_POST(self):
        api_key = os.environ.get("POE_API_KEY")
        default_model = os.environ.get("MODEL_ID", "gpt-4o")
        if not api_key:
            return self._send(500, {"error": "Missing POE_API_KEY"})

        # 读请求体
        try:
            length = int(self.headers.get("content-length", 0) or 0)
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            return self._send(400, {"error": "Invalid JSON body"})

        text = (payload.get("text") or "").strip()
        image_data_url = payload.get("imageDataUrl")
        model = payload.get("model") or default_model

        content = []
        if text:
            content.append({"type": "text", "text": text})
        if image_data_url:
            content.append({"type": "image_url", "image_url": {"url": image_data_url}})
        if not content:
            return self._send(400, {"error": "缺少文本或图片"})

        req_body = {
            "model": model,
            "messages": [
                {"role": "system", "content": "你是一个严谨的中文助理，善于从用户上传的图片和文本中提炼要点，给出可执行建议。"},
                {"role": "user", "content": content}
            ],
            "temperature": 0.4
        }

        data = json.dumps(req_body).encode("utf-8")
        req = urllib.request.Request(POE_URL, data=data, method="POST")
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_data = resp.read().decode("utf-8")
                # Poe 返回的是 OpenAI chat.completions 兼容格式
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
