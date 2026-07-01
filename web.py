from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import json
import base64
from datetime import datetime
from pathlib import Path
from core.assistant import AIAssistant
from core.llm import LLM

app = FastAPI()
ai = AIAssistant()
llm = LLM()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "chat_history.json"
SETTINGS_FILE = Path("user_settings.json")

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"theme": "dark", "name": "You", "ai_name": "Aria"}

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

THEMES = {
    "dark": {"bg":"#212121","header":"#171717","text":"#ececec","muted":"#8e8e8e","bubble_ai":"#2d2d2d","bubble_user":"#10a37f","accent":"#10a37f","border":"#2d2d2d","input_bg":"#2d2d2d"},
    "light": {"bg":"#ffffff","header":"#f7f7f8","text":"#202124","muted":"#6e6e80","bubble_ai":"#f1f3f4","bubble_user":"#10a37f","accent":"#10a37f","border":"#e0e0e0","input_bg":"#f7f7f8"},
    "blue": {"bg":"#0a1929","header":"#061020","text":"#e3f2fd","muted":"#90caf9","bubble_ai":"#102a43","bubble_user":"#1976d2","accent":"#42a5f5","border":"#1e3a5f","input_bg":"#102a43"},
    "purple": {"bg":"#1a0a2e","header":"#0f0520","text":"#f3e5f5","muted":"#ce93d8","bubble_ai":"#2d1b4e","bubble_user":"#7b1fa2","accent":"#ab47bc","border":"#3d2466","input_bg":"#2d1b4e"},
    "green": {"bg":"#0d1f0d","header":"#051405","text":"#e8f5e9","muted":"#81c784","bubble_ai":"#1b3a1b","bubble_user":"#2e7d32","accent":"#4caf50","border":"#2d4a2d","input_bg":"#1b3a1b"},
    "sunset": {"bg":"#2d1810","header":"#1a0e08","text":"#fff3e0","muted":"#ffb74d","bubble_ai":"#3d2418","bubble_user":"#e65100","accent":"#ff9800","border":"#4d2e1c","input_bg":"#3d2418"}
}

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Assistant</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; overflow: hidden; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg); color: var(--text); display: flex; flex-direction: column; }
:root { --bg:#212121;--header:#171717;--text:#ececec;--muted:#8e8e8e;--bubble-ai:#2d2d2d;--bubble-user:#10a37f;--accent:#10a37f;--border:#2d2d2d;--input-bg:#2d2d2d; }
.header { background: var(--header); padding: 12px 20px;
  display: flex; align-items: center; gap: 12px;
  border-bottom: 1px solid var(--border); z-index: 10; }
.logo { width: 32px; height: 32px; background: var(--accent);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 16px; color: white; }
.header-text h1 { font-size: 16px; font-weight: 600; }
.header-text p { font-size: 11px; color: var(--muted); }
.header-actions { margin-left: auto; display: flex; gap: 8px; }
.icon-btn { background: transparent; border: 1px solid var(--border);
  color: var(--text); padding: 8px 12px; border-radius: 8px;
  cursor: pointer; font-size: 13px; transition: all 0.2s; }
.icon-btn:hover { background: var(--accent); color: white; border-color: var(--accent); }
.chat { flex: 1; overflow-y: auto; padding: 20px; scroll-behavior: smooth; }
.chat::-webkit-scrollbar { width: 6px; }
.chat::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
.welcome { text-align: center; padding: 60px 20px; max-width: 600px; margin: 0 auto; }
.welcome h2 { font-size: 28px; font-weight: 600; margin-bottom: 10px; color: var(--accent); }
.welcome p { color: var(--muted); font-size: 14px; }
.suggestions { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px; margin-top: 30px; }
.sug-btn { background: var(--input-bg); border: 1px solid var(--border);
  color: var(--text); padding: 12px 16px; border-radius: 10px;
  font-size: 13px; cursor: pointer; text-align: left; transition: all 0.2s; }
.sug-btn:hover { border-color: var(--accent); transform: translateY(-2px); }
.msg { display: flex; gap: 12px; padding: 16px 20px;
  max-width: 800px; margin: 0 auto; animation: slide 0.3s; }
@keyframes slide { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.avatar { width: 32px; height: 32px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0; font-weight: 600; }
.user .avatar { background: var(--accent); color: white; }
.ai .avatar { background: var(--bubble-user); color: white; }
.bubble { flex: 1; line-height: 1.6; font-size: 15px; padding: 12px 16px;
  border-radius: 12px; background: var(--bubble-ai); }
.user .bubble { background: var(--bubble-user); color: white; }
.bubble p { margin: 0; white-space: pre-wrap; }
.bubble img { max-width: 100%; border-radius: 8px; margin-top: 8px; }
.bubble .file-badge { display: inline-block; padding: 4px 10px;
  background: var(--accent); color: white; border-radius: 6px;
  font-size: 12px; margin-top: 6px; }
.input-area { padding: 12px 20px 20px;
  background: linear-gradient(to top, var(--bg) 70%, transparent); }
.input-box { max-width: 800px; margin: 0 auto; display: flex; align-items: flex-end;
  gap: 8px; background: var(--input-bg); border: 1px solid var(--border);
  border-radius: 24px; padding: 8px 12px; transition: border 0.2s; }
.input-box:focus-within { border-color: var(--accent); }
.attach-btn { background: transparent; border: none; color: var(--muted);
  font-size: 20px; cursor: pointer; padding: 4px 8px; }
.attach-btn:hover { color: var(--accent); }
.input-box textarea { flex: 1; background: transparent; border: none;
  color: var(--text); font-size: 15px; resize: none; max-height: 200px;
  padding: 8px; font-family: inherit; outline: none; }
.input-box button { background: var(--accent); color: white; border: none;
  width: 36px; height: 36px; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center; font-size: 18px; }
.input-box button:disabled { background: var(--border); cursor: not-allowed; }
.preview { max-width: 800px; margin: 0 auto 8px; padding: 8px;
  background: var(--input-bg); border-radius: 12px; display: none; }
.preview.active { display: flex; align-items: center; gap: 10px; }
.preview img { max-height: 60px; border-radius: 6px; }
.preview .name { flex: 1; font-size: 13px; color: var(--muted); }
.preview .remove { background: var(--border); border: none; color: var(--text);
  width: 24px; height: 24px; border-radius: 50%; cursor: pointer; }
.typing { display: inline-flex; gap: 4px; padding: 8px 0; }
.typing span { width: 8px; height: 8px; background: var(--muted);
  border-radius: 50%; animation: bounce 1.4s infinite; }
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-8px); opacity: 1; } }
.modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); z-index: 100; align-items: center; justify-content: center; padding: 20px; }
.modal.active { display: flex; }
.modal-box { background: var(--header); border-radius: 16px; padding: 24px;
  max-width: 500px; width: 100%; max-height: 80vh; overflow-y: auto; }
.modal h2 { margin-bottom: 16px; font-size: 20px; }
.modal-close { float: right; background: none; border: none;
  color: var(--text); font-size: 24px; cursor: pointer; }
.setting-group { margin-bottom: 16px; }
.setting-group label { display: block; margin-bottom: 6px;
  color: var(--muted); font-size: 13px; }
.setting-group input, .setting-group select { width: 100%; padding: 10px;
  background: var(--input-bg); border: 1px solid var(--border);
  border-radius: 8px; color: var(--text); font-size: 14px; }
.themes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.theme-btn { padding: 20px 10px; border-radius: 10px; cursor: pointer;
  border: 2px solid transparent; font-size: 12px; font-weight: 600;
  text-align: center; transition: all 0.2s; }
.theme-btn.active { border-color: var(--accent); }
.btn { background: var(--accent); color: white; border: none;
  padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px;
  margin-right: 8px; margin-top: 8px; }
.btn.secondary { background: var(--border); }
@media (max-width: 600px) {
  .msg { padding: 12px; }
  .welcome { padding: 30px 15px; }
  .welcome h2 { font-size: 22px; }
  .suggestions { grid-template-columns: 1fr; }
  .themes { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>
<div class="header">
  <div class="logo">AI</div>
  <div class="header-text">
    <h1 id="ai-name">AI Assistant</h1>
    <p id="status-text">Online</p>
  </div>
  <div class="header-actions">
    <button class="icon-btn" onclick="openHistory()">History</button>
    <button class="icon-btn" onclick="openSettings()">Settings</button>
    <button class="icon-btn" onclick="newChat()">New</button>
  </div>
</div>
<div class="chat" id="chat">
  <div class="welcome" id="welcome">
    <h2>How can I help you today?</h2>
    <p>Upload images, files, or just chat</p>
    <div class="suggestions">
      <button class="sug-btn" onclick="ask(this)">Explain quantum computing simply</button>
      <button class="sug-btn" onclick="ask(this)">Analyze this image for me</button>
      <button class="sug-btn" onclick="ask(this)">Help me write code</button>
      <button class="sug-btn" onclick="ask(this)">Summarize a document</button>
    </div>
  </div>
</div>
<div class="preview" id="preview">
  <img id="previewImg" style="display:none">
  <span class="name" id="previewName"></span>
  <button class="remove" onclick="removeFile()">X</button>
</div>
<div class="input-area">
  <div class="input-box">
    <button class="attach-btn" onclick="document.getElementById('fileInput').click()">+</button>
    <input type="file" id="fileInput" style="display:none" accept="image/*,.pdf,.txt,.md,.py,.js,.html,.css,.json" onchange="handleFile(event)">
    <textarea id="input" placeholder="Message AI Assistant... (Shift+Enter for new line)" rows="1"></textarea>
    <button id="send" onclick="send()">&#10148;</button>
  </div>
</div>

<div class="modal" id="settingsModal">
  <div class="modal-box">
    <button class="modal-close" onclick="closeSettings()">&times;</button>
    <h2>Settings</h2>
    <div class="setting-group">
      <label>Your Name</label>
      <input type="text" id="userName" placeholder="Your name">
    </div>
    <div class="setting-group">
      <label>AI Name</label>
      <input type="text" id="aiNameInput" placeholder="AI's name">
    </div>
    <div class="setting-group">
      <label>Theme</label>
      <div class="themes" id="themes">
        <div class="theme-btn" data-theme="dark" style="background:#212121;color:#ececec">Dark</div>
        <div class="theme-btn" data-theme="light" style="background:#fff;color:#202124">Light</div>
        <div class="theme-btn" data-theme="blue" style="background:#0a1929;color:#e3f2fd">Blue</div>
        <div class="theme-btn" data-theme="purple" style="background:#1a0a2e;color:#f3e5f5">Purple</div>
        <div class="theme-btn" data-theme="green" style="background:#0d1f0d;color:#e8f5e9">Green</div>
        <div class="theme-btn" data-theme="sunset" style="background:#2d1810;color:#fff3e0">Sunset</div>
      </div>
    </div>
    <div class="setting-group">
      <label>Storage</label>
      <div>
        <button class="btn" onclick="exportData()">Export Chat</button>
        <button class="btn secondary" onclick="clearHistory()">Clear All</button>
      </div>
    </div>
  </div>
</div>

<div class="modal" id="historyModal">
  <div class="modal-box">
    <button class="modal-close" onclick="closeHistory()">&times;</button>
    <h2>Chat History</h2>
    <div id="historyList"></div>
  </div>
</div>

<script>
const THEMES = """ + json.dumps(THEMES) + """;
let settings = { theme: 'dark', name: 'You', ai_name: 'Aria' };
let history = [];
let sid = 'web-' + Date.now();
let busy = false;
let attachedFile = null;

async function init() {
  try {
    const r = await fetch('/api/settings');
    settings = await r.json();
  } catch(e) {}
  applyTheme(settings.theme);
  document.getElementById('userName').value = settings.name;
  document.getElementById('aiNameInput').value = settings.ai_name;
  document.getElementById('ai-name').textContent = settings.ai_name || 'AI Assistant';
  try {
    const r = await fetch('/api/history');
    history = await r.json();
  } catch(e) {}
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.onclick = () => {
      settings.theme = btn.dataset.theme;
      applyTheme(settings.theme);
      saveSettings();
    };
  });
}

function applyTheme(theme) {
  const t = THEMES[theme] || THEMES.dark;
  const root = document.documentElement;
  Object.keys(t).forEach(k => root.style.setProperty('--' + k.replace('_','-'), t[k]));
  document.querySelectorAll('.theme-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.theme === theme);
  });
}

async function saveSettings() {
  settings.name = document.getElementById('userName').value || 'You';
  settings.ai_name = document.getElementById('aiNameInput').value || 'Aria';
  document.getElementById('ai-name').textContent = settings.ai_name;
  try { await fetch('/api/settings', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(settings)}); } catch(e) {}
}

function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  attachedFile = file;
  const preview = document.getElementById('preview');
  const previewImg = document.getElementById('previewImg');
  const previewName = document.getElementById('previewName');
  if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewImg.style.display = 'block';
      previewName.textContent = file.name;
      preview.classList.add('active');
    };
    reader.readAsDataURL(file);
  } else {
    previewImg.style.display = 'none';
    previewName.textContent = file.name + ' (' + (file.size/1024).toFixed(1) + ' KB)';
    preview.classList.add('active');
  }
}

function removeFile() {
  attachedFile = null;
  document.getElementById('preview').classList.remove('active');
  document.getElementById('fileInput').value = '';
}

function addMsg(html, role) {
  const welcome = document.getElementById('welcome');
  if (welcome) welcome.remove();
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  const av = document.createElement('div');
  av.className = 'avatar';
  av.textContent = role === 'user' ? (settings.name || 'U')[0].toUpperCase() : (settings.ai_name || 'AI')[0].toUpperCase();
  const bub = document.createElement('div');
  bub.className = 'bubble';
  bub.innerHTML = html;
  div.appendChild(av);
  div.appendChild(bub);
  document.getElementById('chat').appendChild(div);
  document.getElementById('chat').scrollTop = 999999;
}

function addTyping() {
  const div = document.createElement('div');
  div.className = 'msg ai';
  div.id = 'typing';
  div.innerHTML = '<div class="avatar">' + (settings.ai_name || 'AI')[0].toUpperCase() + '</div><div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  document.getElementById('chat').appendChild(div);
  document.getElementById('chat').scrollTop = 999999;
}

function removeTyping() { const t = document.getElementById('typing'); if (t) t.remove(); }

function escape(text) { return String(text).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

async function send() {
  if (busy) return;
  const text = document.getElementById('input').value.trim();
  if (!text && !attachedFile) return;
  busy = true;
  document.getElementById('send').disabled = true;

  // Build user message HTML
  let userHtml = '';
  if (attachedFile) {
    if (attachedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = async (e) => {
        userHtml = '<p>' + escape(text) + '</p><img src="' + e.target.result + '">';
        await doSend(text, userHtml);
      };
      reader.readAsDataURL(attachedFile);
      return;
    } else {
      userHtml = '<p>' + escape(text) + '</p><span class="file-badge">File: ' + escape(attachedFile.name) + '</span>';
    }
  } else {
    userHtml = '<p>' + escape(text) + '</p>';
  }
  await doSend(text, userHtml);
}

async function doSend(text, userHtml) {
  addMsg(userHtml, 'user');
  document.getElementById('input').value = '';
  document.getElementById('input').style.height = 'auto';
  addTyping();

  try {
    const formData = new FormData();
    formData.append('message', text);
    formData.append('session_id', sid);
    if (attachedFile) {
      formData.append('file', attachedFile);
    }

    const r = await fetch('/chat', { method: 'POST', body: formData });
    const d = await r.json();
    removeTyping();
    addMsg('<p>' + escape(d.reply || d.error || 'No response') + '</p>', 'ai');

    // Save to history
    fetch('/api/history').then(r => r.json()).then(h => history = h);
  } catch (e) {
    removeTyping();
    addMsg('<p>Error: ' + escape(e.message) + '</p>', 'ai');
  }
  busy = false;
  document.getElementById('send').disabled = false;
  removeFile();
  document.getElementById('input').focus();
}

function ask(btn) { document.getElementById('input').value = btn.textContent; send(); }
function openSettings() { document.getElementById('settingsModal').classList.add('active'); }
function closeSettings() { saveSettings(); document.getElementById('settingsModal').classList.remove('active'); }
function openHistory() { renderHistory(); document.getElementById('historyModal').classList.add('active'); }
function closeHistory() { document.getElementById('historyModal').classList.remove('active'); }

function renderHistory() {
  const list = document.getElementById('historyList');
  if (!history.length) {
    list.innerHTML = '<p style="color:var(--muted);padding:20px;text-align:center">No history yet</p>';
    return;
  }
  list.innerHTML = history.slice().reverse().map((h, i) => `
    <div style="padding:12px;border-bottom:1px solid var(--border);cursor:pointer" onclick="loadHistory(${history.length-1-i})">
      <div style="font-size:12px;color:var(--muted)">${h.date||''}</div>
      <div style="margin-top:4px"><b>You:</b> ${escape((h.user||'').substring(0,80))}</div>
      <div style="margin-top:4px;color:var(--muted)"><b>AI:</b> ${escape((h.ai||'').substring(0,80))}</div>
    </div>
  `).join('');
}

function loadHistory(idx) {
  const h = history[idx];
  if (!h) return;
  document.getElementById('chat').innerHTML = '';
  addMsg('<p>' + escape(h.user) + '</p>', 'user');
  addMsg('<p>' + escape(h.ai) + '</p>', 'ai');
  closeHistory();
}

function newChat() {
  if (confirm('Start a new chat?')) {
    sid = 'web-' + Date.now();
    document.getElementById('chat').innerHTML = '<div class="welcome" id="welcome"><h2>New Chat</h2><p>How can I help?</p></div>';
  }
}

async function clearHistory() {
  if (confirm('Delete ALL history?')) {
    await fetch('/api/history', {method: 'DELETE'});
    history = [];
    closeSettings();
  }
}

function exportData() {
  const data = JSON.stringify(history, null, 2);
  const blob = new Blob([data], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'ai-chat-' + new Date().toISOString().split('T')[0] + '.json';
  a.click();
}

document.getElementById('send').onclick = send;
document.getElementById('input').addEventListener('keypress', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
});
document.getElementById('input').addEventListener('input', e => {
  e.target.style.height = 'auto';
  e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
});

init();
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/chat")
async def chat(message: str = Form(""), session_id: str = Form("default"),
              file: UploadFile = File(None)):
    if not message and not file:
        return JSONResponse({"error": "Empty"}, status_code=400)
    try:
        if file:
            contents = await file.read()
            file_type = file.content_type or "text/plain"
            if file_type.startswith("image/"):
                reply = llm.chat_with_image(message or "What's in this image?", contents, file_type)
            else:
                reply = llm.chat_with_file(message, contents, file_type)
        else:
            reply = ai.ask(message)

        # Save to history
        hist = load_history()
        hist.append({
            "user": message + (f" [File: {file.filename}]" if file else ""),
            "ai": reply, "session": session_id,
            "date": datetime.now().isoformat()
        })
        save_history(hist)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/settings")
async def get_settings(): return load_settings()

@app.post("/api/settings")
async def update_settings(request: Request):
    save_settings(await request.json())
    return {"status": "ok"}

@app.get("/api/history")
async def get_history(): return load_history()

@app.delete("/api/history")
async def delete_history():
    save_history([])
    return {"status": "cleared"}

if __name__ == "__main__":
    import config
    print("Server: http://localhost:" + str(config.API_PORT))
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)

