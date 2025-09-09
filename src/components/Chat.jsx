import { useEffect, useState } from 'react'

const AGENTS = [
  { id: 'claude-3-5-sonnet-20240620', name: 'Claude Sonnet 4.0' },
  { id: 'gpt-4o-mini', name: 'GPT‑4o-mini' },
  { id: 'sml-fanhuati.XUANTI', name: '自定义：选题助手' }
]

export default function Chat(){
  const [model, setModel] = useState(AGENTS[0].id)
  const [chats, setChats] = useState(()=>{
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    if (!db.current){
      const id = crypto.randomUUID()
      db.current = id
      db[id] = { id, title: '新的对话', model, created: Date.now(), updated: Date.now(), messages: [] }
      localStorage.setItem('chats', JSON.stringify(db))
      return db
    }
    return db
  })
  const current = chats[chats.current]

  function save(db){ localStorage.setItem('chats', JSON.stringify(db)); setChats(db) }

  async function toDataUrl(file){
    const r = new FileReader()
    return new Promise((ok,no)=>{ r.onerror=no; r.onload=()=>ok(r.result); r.readAsDataURL(file) })
  }

  async function send(){
    const ta = document.getElementById('text')
    const fi = document.getElementById('file')
    const text = ta.value.trim()
    const file = fi.files[0]
    if (!text && !file){ ta.focus(); return }
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    const chat = db[db.current]

    let userContent = text
    if (file){
      const url = await toDataUrl(file)
      userContent = [
        { type:'text', text: text || '看图说话' },
        { type:'image_url', image_url: { url } }
      ]
    }

    chat.messages.push({ role:'user', content: userContent })
    chat.updated = Date.now()
    save(db)
    ta.value=''; fi.value=''

    const res = await fetch('/api/ask', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ model, messages: chat.messages })
    })
    const data = await res.json().catch(()=>({error:'bad json'}))
    if (!res.ok){
      chat.messages.push({ role:'assistant', content:'调用失败：'+(data?.error||res.status) })
      chat.updated = Date.now(); save(db); return
    }
    const msg = data?.choices?.[0]?.message
    let content = ''
    if (typeof msg?.content === 'string') content = msg.content
    else if (Array.isArray(msg?.content)) content = msg.content.map(p=>p.type==='text'?p.text:'').join('\n')
    chat.messages.push({ role:'assistant', content: content || '(空响应)' })
    chat.updated = Date.now(); save(db)
  }

  useEffect(()=>{
    document.getElementById('send').onclick = send
    document.getElementById('imgBtn').onclick = ()=>document.getElementById('file').click()
    const ta = document.getElementById('text')
    const h = e=>{ if (e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send() } }
    ta.addEventListener('keydown', h)
    return ()=>ta.removeEventListener('keydown', h)
  }, [model, chats.current])

  function newChat(){
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    const id = crypto.randomUUID()
    db.current = id
    db[id] = { id, title:'新的对话', model, created: Date.now(), updated: Date.now(), messages: [] }
    save(db)
  }

  function switchChat(id){
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    db.current = id; save(db)
  }

  function renameChat(){
    const name = prompt('重命名：', current.title||'')
    if (name==null) return
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    db[db.current].title = name || db[db.current].title
    db[db.current].updated = Date.now(); save(db)
  }

  function delCurrent(){
    const db = JSON.parse(localStorage.getItem('chats')||'{}')
    const ids = Object.keys(db).filter(k=>k!=='current')
    const idx = ids.indexOf(db.current)
    delete db[db.current]
    const left = Object.keys(db).filter(k=>k!=='current')
    if (left.length){
      db.current = left[0]
    } else {
      const id = crypto.randomUUID()
      db.current = id
      db[id] = { id, title:'新的对话', model, created: Date.now(), updated: Date.now(), messages: [] }
    }
    save(db)
  }

  const list = Object.keys(chats).filter(k=>k!=='current').map(k=>chats[k]).sort((a,b)=>b.updated-a.updated)

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="side-top">
          <button className="btn primary" onClick={newChat}>＋ 新建对话</button>
          <button className="btn" onClick={renameChat}>重命名</button>
          <button className="btn" onClick={delCurrent}>删除</button>
        </div>
        <div className="chats">
          {list.map(c=>(
            <div key={c.id} className={'chat-item'+(c.id===chats.current?' active':'')} onClick={()=>switchChat(c.id)}>
              {c.title}
            </div>
          ))}
        </div>
        <div className="side-top">
          <span className="badge">本地保存 · 多智能体</span>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div>ChatGPT风格 · <span className="badge">模型</span></div>
          <select value={model} onChange={e=>setModel(e.target.value)}>
            {AGENTS.map(a=><option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>

        <div className="chat" id="chat">
          {current.messages.map((m,i)=>(
            <div key={i} className={'row '+(m.role==='user'?'me':'asst')}>
              <div className="avatar">{m.role==='user'?'🧑':'🤖'}</div>
              <div className="bubble">
                <div className="meta">{m.role==='user'?'你':'助手'}</div>
                {Array.isArray(m.content)
                  ? <div>{m.content.find(p=>p.type==='text')?.text || ''}{m.content.find(p=>p.type==='image_url')?.image_url?.url && <img src={m.content.find(p=>p.type==='image_url').image_url.url} alt="" />}</div>
                  : <div>{m.content}</div>}
              </div>
            </div>
          ))}
        </div>

        <div className="composer">
          <div className="composer-inner">
            <textarea id="text" className="textarea" placeholder="输入消息，Enter 发送，Shift+Enter 换行"></textarea>
            <input id="file" type="file" accept="image/*" className="file-hidden">
            <button id="imgBtn" className="btn">🖼 图片</button>
            <button id="send" className="btn primary">发送</button>
          </div>
        </div>
      </main>
    </div>
  )
}
