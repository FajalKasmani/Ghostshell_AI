import socket, threading, os, time, webbrowser, paramiko
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- CONFIG ---
WEB_PORT = 5050
SSH_PORT = 2222
LOG_FILE = "attacks.csv"

# --- THE AGENT CORE (Ye hai asli Agents ka logic) ---
class AgentCore:
    def __init__(self):
        self.stats = {"Architect": 0, "PuppetMaster": 0, "Watcher": 0}

    def decide(self, cmd):
        cmd = cmd.strip().lower()
        self.stats["Watcher"] += 1
        
        # Architect Agent handle karega Filesystem commands
        if cmd in ["ls", "dir", "pwd", "cd"]:
            self.stats["Architect"] += 1
            return "total 104\n-rw-r---- 1 root root 2048 secret_db.sql\n-r-------- 1 root root 1024 master_key.txt", \
                   "Architect Agent", \
                   "Logic: Hacker is looking for data. I am generating a fake directory to keep them trapped in the sandbox."
        
        # Puppet Master handles Identity & Permissions
        elif cmd in ["whoami", "id", "sudo", "su"]:
            self.stats["PuppetMaster"] += 1
            return "root", "Puppet Master Agent", \
                   "Logic: Hacker wants privilege escalation. I am spoofing 'root' identity to monitor their next move safely."
        
        # Generic fallback
        else:
            return f"bash: {cmd}: command recorded and filtered.", "Watcher Agent", \
                   "Logic: Unknown command detected. Logging behavioral pattern for threat intelligence."

brain = AgentCore()

# --- PROFESSIONAL DASHBOARD UI ---
class SOCDashboard(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        # Read Logs
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = [line.strip().split('|') for line in f.readlines()]
        
        # Chart Calculation
        total = max(len(logs), 1)
        arc_h = (brain.stats['Architect'] / total) * 100
        pup_h = (brain.stats['PuppetMaster'] / total) * 100
        wat_h = (brain.stats['Watcher'] / total) * 100

        rows = ""
        for p in reversed(logs[-6:]):
            if len(p) == 5:
                rows += f"""
                <div class="card shadow">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="badge">{p[3]}</span>
                        <small style="color:#666">{p[0]}</small>
                    </div>
                    <p><b>Hacker typed:</b> <code>{p[2]}</code></p>
                    <div class="thought"><strong>Agent Thought:</strong> {p[4]}</div>
                </div>"""

        html = f"""
        <!DOCTYPE html>
        <html><head>
            <title>Labyrinth AI | Hackathon SOC</title>
            <meta http-equiv="refresh" content="2">
            <style>
                :root {{ --neon: #00FF41; --bg: #050505; --panel: #111; }}
                body {{ background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }}
                .header {{ background: #000; padding: 20px 50px; border-bottom: 2px solid var(--neon); display: flex; justify-content: space-between; align-items: center; }}
                .main {{ display: grid; grid-template-columns: 300px 1fr; gap: 20px; padding: 20px; flex: 1; }}
                
                /* Sidebar Charts */
                .sidebar {{ display: flex; flex-direction: column; gap: 20px; }}
                .stat-box {{ background: var(--panel); padding: 20px; border-radius: 10px; border: 1px solid #333; }}
                .bar-container {{ margin-top: 15px; background: #222; height: 10px; border-radius: 5px; overflow: hidden; }}
                .bar {{ background: var(--neon); height: 100%; box-shadow: 0 0 10px var(--neon); transition: 0.5s; }}
                
                /* Feed */
                .feed {{ overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }}
                .card {{ background: #0c0c0c; border: 1px solid #222; padding: 15px; border-radius: 8px; border-left: 4px solid var(--neon); }}
                .badge {{ background: var(--neon); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
                .thought {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #222; color: #aaa; font-style: italic; font-size: 13px; }}
                code {{ color: #ffca28; background: #000; padding: 2px 5px; }}
                
                .blink {{ animation: b 1s infinite; color: red; }}
                @keyframes b {{ 50% {{ opacity: 0; }} }}
            </style>
        </head><body>
            <div class="header">
                <h1 style="margin:0; letter-spacing:3px;">🛡️ LABYRINTH AI</h1>
                <div>STATUS: <span class="blink">● ENFORCING DECEPTION</span></div>
            </div>
            <div class="main">
                <div class="sidebar">
                    <div class="stat-box">
                        <h4 style="margin:0; color:#888;">INTRUSIONS</h4>
                        <h2 style="margin:10px 0; font-size:36px; color:var(--neon);">{len(logs)}</h2>
                    </div>
                    <div class="stat-box">
                        <h4 style="margin:0 0 15px 0; color:#888;">AGENT WORKLOAD</h4>
                        <small>Architect Agent ({int(arc_h)}%)</small><div class="bar-container"><div class="bar" style="width:{arc_h}%"></div></div>
                        <br><small>Puppet Master ({int(pup_h)}%)</small><div class="bar-container"><div class="bar" style="width:{pup_h}%"></div></div>
                        <br><small>Watcher Agent ({int(wat_h)}%)</small><div class="bar-container"><div class="bar" style="width:{wat_h}%"></div></div>
                    </div>
                </div>
                <div class="feed">
                    <h3 style="margin:0; color:#666; font-size:14px;">LIVE AGENT REASONING FEED</h3>
                    {rows if rows else "<p style='color:#444; text-align:center; margin-top:100px;'>Waiting for attack on port 2222...</p>"}
                </div>
            </div>
            <footer style="text-align:center; padding:10px; font-size:12px; color:#444; border-top:1px solid #222;">
                GhostShell Project | Autonomous Cyber Defense
            </footer>
        </body></html>
        """
        self.wfile.write(html.encode())

# --- SSH SERVER ---
def start_ssh():
    class S(paramiko.ServerInterface):
        def check_auth_password(self, u, p): return paramiko.AUTH_SUCCESSFUL
        def check_channel_request(self, k, c): return paramiko.OPEN_SUCCEEDED

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', SSH_PORT))
    sock.listen(5)
    while True:
        c, addr = sock.accept()
        def session():
            try:
                t = paramiko.Transport(c)
                t.add_server_key(paramiko.RSAKey.generate(2048))
                t.start_server(server=S())
                chan = t.accept(20)
                if chan:
                    chan.send("\r\n[SYSTEM: LABYRINTH AI CORE ACTIVE]\r\n$ ")
                    while True:
                        cmd = chan.recv(1024).decode().strip()
                        if not cmd: break
                        # Agents at work
                        res, agent, thought = brain.decide(cmd)
                        with open(LOG_FILE, "a") as f:
                            f.write(f"{datetime.now().strftime('%H:%M:%S')}|SSH|{cmd}|{agent}|{thought}\n")
                        chan.send(f"\r\n{res}\r\n$ ")
            except: pass
        threading.Thread(target=session).start()

if __name__ == "__main__":
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    open(LOG_FILE, 'w').close()
    threading.Thread(target=start_ssh, daemon=True).start()
    print(f"[*] Dashboard: http://localhost:{WEB_PORT}")
    webbrowser.open(f"http://localhost:{WEB_PORT}")
    HTTPServer(('0.0.0.0', WEB_PORT), SOCDashboard).serve_forever()