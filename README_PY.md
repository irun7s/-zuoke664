# Python 版（Vercel Functions）

## 目录结构
```
/index.html
/api/ask.py
/requirements.txt
```

## 怎么部署
1. 把这三个文件**放在仓库根目录**（不是子目录）。
2. 在 Vercel 导入这个仓库，不用任何 Build 命令。
3. Vercel → Settings → Environment Variables 添加：
   - `POE_API_KEY`：你的 Poe API Key
   - `MODEL_ID`（可选）：`gpt-4o` 或 `claude-3.5-sonnet`
   勾选 Production/Preview/Development，保存后 **Redeploy**。
4. 访问 `https://你的域名/api/ask`：应返回 405 或 `Only POST allowed`（如果你用 GET 访问）；前端调用用 POST。

## 说明
- 这是 Vercel 的 **Python 运行时**，入口是 `api/*.py`，里面定义了继承 `BaseHTTPRequestHandler` 的 `handler` 类即可。官方文档：Python Runtime。

