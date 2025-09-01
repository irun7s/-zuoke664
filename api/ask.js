export const config = { runtime: 'nodejs' };


export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Only POST allowed' });
  }

  const POE_API_KEY = process.env.POE_API_KEY;
  const DEFAULT_MODEL = process.env.MODEL_ID || 'gpt-4o';
  if (!POE_API_KEY) {
    return res.status(500).json({ error: 'Missing POE_API_KEY' });
  }

  try {
    const { text = '', imageDataUrl = null, model } = req.body || {};
    const modelId = model || DEFAULT_MODEL;

    const content = [];
    if (text) content.push({ type: 'text', text });
    if (imageDataUrl) content.push({ type: 'image_url', image_url: { url: imageDataUrl } });
    if (content.length === 0) {
      return res.status(400).json({ error: '缺少文本或图片' });
    }

    const payload = {
      model: modelId,
      messages: [
        { role: 'system', content: '你是一个严谨的中文助理，善于从用户上传的图片和文本中提炼要点，给出可执行建议。' },
        { role: 'user', content }
      ],
      temperature: 0.4
    };

    const r = await fetch('https://api.poe.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${POE_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await r.json();
    res.status(r.ok ? 200 : r.status).json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
