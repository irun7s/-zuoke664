from http.server import BaseHTTPRequestHandler
import os, json
import openai

# 初始化 Poe SDK 客户端
client = openai.OpenAI(
    api_key=os.getenv("POE_API_KEY"),   # 需要在 Vercel/服务器里配置环境变量
    base_url="https://api.poe.com/v1",
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

    def do_POST(self):
        try:
            length = int(self.headers.get("content-length", 0) or 0)
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            payload = json.loads(body)
        except Exception:
            return self._send(400, {"error": "Invalid JSON body"})

        # 获取模型，前端传的优先，其次环境变量，最后一个默认
        model = payload.get("model") or os.getenv("POE_MODEL") or "sml-fanhuati.XUANTI"

        messages = payload.get("messages")
        if not messages:
            text = (payload.get("text") or "").strip()
            if not text:
                return self._send(400, {"error": "Missing 'messages' or 'text'"})
            messages = [{"role": "user", "content": text}]

        try:
            # 调用 Poe 官方 SDK
            chat = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=payload.get("temperature", 0.4),
                max_tokens=payload.get("max_tokens", 1024),
            )
            return self._send(200, chat.to_dict())
        except Exception as e:
            return self._send(500, {"error": str(e)})
