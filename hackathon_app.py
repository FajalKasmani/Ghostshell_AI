import socket, threading, os, time, webbrowser, paramiko
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- CONFIG ---
WEB_PORT = 5050
SSH_PORT = 2222
LOG_FILE = "attacks.csv"

class AgentOrchestrator:
    def __init__(self):
        self.stats = {"Architect": 0, "PuppetMaster": 0, "Watcher": 0}

    def analyze_and_respond(self, cmd):
        cmd = cmd.strip().lower()
        self.stats["Watcher"] += 1
        if cmd in ["ls", "dir", "pwd"]:
            self.stats["Architect"] += 1
            return "total 104\n-rw-r---- 1 root root 2048 secret_db.sql", "ARCHITECT AGENT", "THOUGHT: Hacker seeking files. Redirecting to virtual honey-pot."
        elif cmd in ["whoami", "id"]:
            self.stats["PuppetMaster"] += 1
            return "root", "PUPPET MASTER", "THOUGHT: Spoofing superuser identity to gain behavioral intelligence."
        else:
            return "Access denied.", "WATCHER AGENT", "THOUGHT: Command filtered. Logging intruder pattern."

brain = AgentOrchestrator()

class SOCDashboard(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = [line.strip().split('|') for line in f.readlines() if '|' in line]
        
        total = max(len(logs), 1)
        arc_w = (brain.stats['Architect'] / total) * 100
        pup_w = (brain.stats['PuppetMaster'] / total) * 100
        wat_w = (brain.stats['Watcher'] / total) * 100

        feed_html = ""
        for p in reversed(logs[-6:]):
            if len(p) >= 5:
                feed_html += f"""
                <div style="background:#000; border-left:4px solid #00FF41; padding:15px; margin-bottom:10px; border-radius:5px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px;">
                        <span style="background:#00FF41; color:black; padding:2px 8px; font-weight:bold;">{p[3]}</span>
                        <span style="color:#555;">{p[0]}</span>
                    </div>
                    <div style="margin:10px 0;"><strong>CMD:</strong> <code>{p[2]}</code></div>
                    <div style="color:#888; font-style:italic; font-size:13px; border-top:1px solid #222; padding-top:5px;">{p[4]}</div>
                </div>"""

        html = f"""
        <html><head><meta http-equiv="refresh" content="2">
        <style>
            body {{ background:#050505; color:white; font-family:sans-serif; margin:0; padding:20px; }}
            .grid {{ display: grid; grid-template-columns: 300px 1fr; gap: 20px; }}
            .card {{ background:#111; border:1px solid #333; padding:20px; border-radius:10px; }}
            .bar {{ background:#222; height:10px; border-radius:5px; margin:10px 0; overflow:hidden; }}
            .fill {{ background:#00FF41; height:100%; box-shadow:0 0 10px #00FF41; transition:0.5s; }}
        </style></head>
        <body>
            <h1 style="color:#00FF41; border-bottom:2px solid #00FF41; padding-bottom:10px;">🛡️ LABYRINTH AI SOC</h1>
            <div class="grid">
                <div class="sidebar">
                    <div class="card">
                        <h3>THREATS: {len(logs)}</h3>
                        <p style="font-size:12px; color:#666;">AGENT WORKLOAD</p>
                        Architect <div class="bar"><div class="fill" style="width:{arc_w}%"></div></div>
                        PuppetMaster <div class="bar"><div class="fill" style="width:{pup_w}%"></div></div>
                        Watcher <div class="bar"><div class="fill" style="width:{wat_w}%"></div></div>
                    </div>
                </div>
                <div class="card">
                    <h3 style="color:#666;">LIVE AGENT REASONING STREAM</h3>
                    {feed_html if feed_html else "<p style='color:#333;'>SYSTEM READY: Connect via SSH (Port 2222) to see AI Agents in action.</p>"}
                </div>
            </div>
        </body></html>
        """
        self.wfile.write(html.encode())

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
                t = paramiko.Transport(c); t.add_server_key(paramiko.RSAKey.generate(2048))
                t.start_server(server=S()); chan = t.accept(20)
                if chan:
                    chan.send("\r\n[LABYRINTH AI ONLINE]\r\n$ ")
                    while True:
                        cmd = chan.recv(1024).decode().strip()
                        if not cmd: break
                        res, agent, thought = brain.analyze_and_respond(cmd)
                        with open(LOG_FILE, "a") as f: f.write(f"{datetime.now().strftime('%H:%M:%S')}|SSH|{cmd}|{agent}|{thought}\n")
                        chan.send(f"\r\n{res}\r\n$ ")
            except: pass
        threading.Thread(target=session).start()

if __name__ == "__main__":
    if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
    open(LOG_FILE, 'w').close()
    threading.Thread(target=start_ssh, daemon=True).start()
    webbrowser.open(f"http://localhost:{WEB_PORT}")
    HTTPServer(('0.0.0.0', WEB_PORT), SOCDashboard).serve_forever()