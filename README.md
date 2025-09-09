# Vercel 部署：ChatGPT风格 + Poe API

## 结构
- 前端：Vite + React（`index.html`、`/src`）
- 后端：Python Serverless（`/api/ask.py`，Poe SDK）
- 配置：`vercel.json`

## 部署（GitHub → Vercel）
1. 新建 GitHub 仓库，把本项目所有文件推上去。
2. Vercel → New Project → 选择该仓库。
3. 在 Vercel 项目 Settings → Environment Variables：
   - `POE_API_KEY`：必填
   - `POE_MODEL`：可选，默认 `claude-3-5-sonnet-20240620`
4. Deploy，打开域名测试：`/` 前端，`/api/ask` 接口。

## 本地开发（可选）
- 前端：`npm install && npm run dev` → http://localhost:5173

## 常见问题
- “Missing POE_API_KEY” → 去 Vercel 配环境变量后 Redeploy。
- 想切换你自己的智能体 → 改 `src/components/Chat.js` 的 `AGENTS` 列表或设置环境变量。
