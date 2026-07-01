from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from core.assistant import AIAssistant

app = FastAPI()
ai = AIAssistant()

html = """<html><body style="font-family:Arial;padding:20px"><h1>AI Assistant</h1><div id="m"></div><input id="i" style="width:70%;padding:10px"><button onclick="go()">Send</button><script>function add(t,u){let d=document.createElement('div');d.textContent=t;d.style.background=u?'#667eea':'#eee';d.style.color=u?'white':'black';d.style.padding='10px';d.style.margin='5px';d.style.borderRadius='10px';document.getElementById('m').appendChild(d)}async function go(){let t=document.getElementById('i').value;if(!t)return;add(t,true);document.getElementById('i').value='';let r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t})});let d=await r.json();add(d.reply,false)}document.getElementById('i').addEventListener('keypress',e=>{if(e.key==='Enter')go()})</script></body></html>"""

@app.get("/")
def home():
    return HTMLResponse(html)

@app.post("/chat")
async def chat(req: dict):
    return {"reply": ai.ask(req.get("message", ""))}

if __name__ == "__main__":
    import config
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
