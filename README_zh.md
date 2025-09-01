# 最终版（GitHub + Vercel）

## 目录
```
/index.html
/api/ask.js
(可选)/vercel.json
```

## 部署步骤（超简）
1. 把这三个文件作为**仓库根**上传到 GitHub。
2. Vercel 导入这个仓库，默认设置即可。
3. 在 Vercel → Settings → Environment Variables 添加：
   - `POE_API_KEY`：你的 Poe API Key
   - `MODEL_ID`（可选）：`gpt-4o` 或 `claude-3.5-sonnet`
   三个环境都勾上，然后 Redeploy。
4. 打开 `https://你的域名/api/ask`：看到 `Only POST allowed` 就说明函数已部署。
5. 打开根域名，输入文本/上传图片，点击提交即可。

## 常见问题
- 404：文件不在仓库根；或 Vercel Root Directory 没指对。
- 500 Missing POE_API_KEY：你没配环境变量或没 Redeploy。
- 旧版 now 报错：删除任何 `now.json`，`vercel.json` 只保留现代写法或干脆删掉。

