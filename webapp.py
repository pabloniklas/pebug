# webapp.py
from __future__ import annotations
import os
import re
from typing import List, Optional
from flask import Flask, request, jsonify, render_template_string


# Tu core OO
from modules.Terminal import AnsiColors
from modules.Pebug import Pebug  # <-- tu archivo class-based (el que pegaste)

# -------- ANSI → HTML ----------
ANSI_RE = re.compile(r'\x1b\[(\d+(?:;\d+)*)m')
COLOR_MAP = {
    '30': 'black', '31': 'red', '32': 'green', '33': 'olive', '34': 'navy', '35': 'purple', '36': 'teal', '37': 'silver',
    '90': '#777', '91': '#ff6b6b', '92': '#4caf50', '93': '#ffc107', '94': '#42a5f5', '95': '#ba68c8', '96': '#26c6da', '97': '#f5f5f5',
}


def _esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def ansi_to_html(s: str) -> str:
    out, stack, pos = [], [], 0
    for m in ANSI_RE.finditer(s):
        out.append(_esc(s[pos:m.start()]))
        codes = m.group(1).split(';')
        if '0' in codes:
            while stack:
                out.append('</span>')
                stack.pop()
        else:
            styles = []
            for c in codes:
                if c == '1':
                    styles.append('font-weight:600')
                elif c in COLOR_MAP:
                    styles.append(f'color:{COLOR_MAP[c]}')
            if styles:
                out.append(f'<span style="{";".join(styles)}">')
                stack.append('span')
        pos = m.end()
    out.append(_esc(s[pos:]))
    while stack:
        out.append('</span>')
        stack.pop()
    return ''.join(out)

# -------- Terminal Web (adaptador) ----------


class WebTerminal:
    """
    Implementa la misma interfaz de Terminal pero bufferiza la salida.
    Tip extra: si el texto ya trae ANSI, no le agregamos color para no pisar el trace.
    """

    def __init__(self):
        self.buffer: List[str] = []

    def attach_buffer(self, buf: List[str]):
        self.buffer = buf

    def _w(self, msg="", end="\n", flush=False):
        self.buffer.append(str(msg) + (end or ""))

    def default_message(self, msg="", end="\n", flush=False):
        # salida "tal cual" (lo usa el trace si no se pasa callback)
        self._w(msg, end=end, flush=flush)

    def info_message(self, msg="", detail="", newline=True):
        text = f"{msg}{(' ' + detail) if detail else ''}"
        if "\x1b[" in text:  # ya trae ANSI, no sobrepintar
            self._w(text, end="\n" if newline else "")
        else:
            self._w(AnsiColors.BRIGHT_WHITE.value + text + AnsiColors.RESET.value,
                    end="\n" if newline else "")

    def success_message(self, msg="", end="\n", flush=False):
        self._w(AnsiColors.BRIGHT_GREEN.value + str(msg) +
                AnsiColors.RESET.value, end=end, flush=flush)

    def warning_message(self, msg="", end="\n", flush=False):
        self._w(AnsiColors.BRIGHT_YELLOW.value + str(msg) +
                AnsiColors.RESET.value, end=end, flush=flush)

    def error_message(self, msg="", end="\n", flush=False):
        self._w(AnsiColors.BRIGHT_RED.value + str(msg) +
                AnsiColors.RESET.value, end=end, flush=flush)


# -------- Flask + singleton Pebug ----------
app = Flask(__name__)
_ENGINE: Optional[Pebug] = None
_TERM = WebTerminal()


def engine() -> Pebug:
    global _ENGINE
    if _ENGINE is None:
        disk_file = os.environ.get("PEBUG_WEB_DISK", "pebug_web_disk.bin")
        # Inyectamos nuestro terminal adaptador
        _ENGINE = Pebug(terminal=_TERM, filename=disk_file)
    return _ENGINE


INDEX_HTML = """
<!doctype html><html><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>pebug web</title>
<style>
  :root { color-scheme: dark; }
  body { background:#1e1e1e; color:#ddd; font-family: ui-monospace,Consolas,monospace; }
  .wrap{max-width:980px;margin:2rem auto;padding:0 1rem}
  h1{font-size:1.1rem;color:#9ad}
  #out{background:#111;padding:12px;border-radius:8px;min-height:360px;white-space:pre-wrap}
  .cmd{display:flex;gap:.5rem;margin-top:.75rem}
  input{flex:1;background:#0c0c0c;color:#fff;border:1px solid #333;padding:.6rem .7rem;border-radius:8px}
  button{background:#2c7be5;color:#fff;border:0;padding:.6rem .9rem;border-radius:8px}
  .help{font-size:.85rem;color:#aaa;margin-top:.35rem}
  kbd{background:#333;padding:.1rem .4rem;border-radius:4px}
</style>
</head><body><div class="wrap">
<h1>pebug — web console</h1>
<div id="out"></div>
<div class="cmd"><input id="cmd" placeholder="p mov ax,1   |   t on   |   d 0000 0010   |   a (entrás al modo ensamblado)"><button id="send">Enviar</button></div>
<p class="help">Comandos: <kbd>r</kbd>, <kbd>p ...</kbd>, <kbd>a</kbd> (modo ensamblado), <kbd>t on/off</kbd>, <kbd>d aaaa bbbb</kbd>, <kbd>f</kbd>, <kbd>s</kbd>, <kbd>h</kbd>, <kbd>e</kbd>, <kbd>sp</kbd>, <kbd>b</kbd>, <kbd>v</kbd>, <kbd>n/g/u</kbd>, <kbd>demo</kbd>, <kbd>q</kbd>.</p>
<script>
const out = document.querySelector('#out'), cmd = document.querySelector('#cmd'), btn = document.querySelector('#send');
function append(html){ out.insertAdjacentHTML('beforeend', html); out.scrollTop = out.scrollHeight; }
async function call(path, body){
  const r = await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body||{})});
  return await r.json();
}
async function boot(){
  const res = await call('/api/start', {});
  if(res.html) append(res.html);
}
async function run(){
  const v = cmd.value.trim(); if(!v) return;
  btn.disabled = true;
  try{
    const data = await call('/api/command', {cmd:v});
    append(data.html || '');
    cmd.value='';
  }catch(e){
    append("<div style='color:#ff6b6b'>[web] "+String(e)+"</div>");
  }finally{
    btn.disabled=false; cmd.focus();
  }
}
btn.addEventListener('click', run);
cmd.addEventListener('keydown', e => { if(e.key==='Enter') run(); });
boot(); cmd.focus();
</script>
</div></body></html>
"""


@app.get("/")
def index():
    return render_template_string(INDEX_HTML)


@app.post("/api/start")
def api_start():
    eng = engine()
    buf: List[str] = []
    _TERM.attach_buffer(buf)
    # Sólo llamar start() una vez; si ya está “inicializado” evitamos duplicar banner.
    # Usamos un flag simple: si el motor ya mostró el banner, no repetir.
    if not getattr(eng, "_web_started", False):
        eng.start()
        eng._web_started = True
    text = "".join(buf)
    html = "<pre>" + ansi_to_html(text) + "</pre>"
    return jsonify({"ok": True, "text": text, "html": html})


@app.post("/api/command")
def api_command():
    eng = engine()
    buf: List[str] = []
    _TERM.attach_buffer(buf)

    data = request.get_json(silent=True) or {}
    cmd = (data.get("cmd") or "").strip()

    # Si aún no se llamó a /api/start, iniciamos ahora
    if not getattr(eng, "_web_started", False):
        eng.start()
        eng._web_started = True

    # Ejecutar 1 línea (responde dict con handled/exit/mode)
    result = eng.execute_line(cmd)
    text = "".join(buf)
    html = "<pre>" + ansi_to_html(text) + "</pre>"
    return jsonify({"ok": True, "result": result, "text": text, "html": html})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(
        os.environ.get("PORT", "5000")), debug=True)
