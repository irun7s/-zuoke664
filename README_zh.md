# Poe + Vercel 最简部署

> 小白路线：把这个文件夹上传到 GitHub 仓库，用 Vercel 导入，填 `POE_API_KEY`，立刻上线。

## 步骤

1. **准备仓库**
   - 上传本目录所有文件到你的 GitHub 仓库（保持目录结构，`index.html` 在根目录，`api/ask.js` 在 `api/` 里）。

2. **获取 Poe API Key**
   - 打开 https://poe.com/api_key 登录并生成 API Key。

3. **在 Vercel 部署**
   - 登录 https://vercel.com ，点击 *Add New Project* → *Import Git Repository*，选择刚才的仓库。
   - 构建设置默认即可。
   - 在 *Settings → Environment Variables* 新增：
     - `POE_API_KEY`：粘贴你的 Key
     - `MODEL_ID`（可选）：默认 `gpt-4o`
   - 点击 *Deploy*。部署完成后访问分配的域名。

4. **使用**
   - 页面文本框输入内容（可选上传图片），点击提交。
   - 后端函数会把请求转发到 Poe 的 OpenAI 兼容 Chat Completions API：`POST https://api.poe.com/v1/chat/completions`。

## 目录结构
```
poe_vercel_starter/
├─ index.html      # 前端页面
└─ api/
   └─ ask.js       # 后端 Serverless 函数
```
