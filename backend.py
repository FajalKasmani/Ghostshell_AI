import socket
import paramiko
import threading
from brain import GhostBrain

class FakeSSH(paramiko.ServerInterface):
    def check_auth_password(self, u, p): return paramiko.AUTH_SUCCESSFUL
    def check_channel_request(self, k, c): return paramiko.OPEN_SUCCEEDED

def handle_ssh(client):
    brain = GhostBrain()
    try:
        t = paramiko.Transport(client)
        t.add_server_key(paramiko.RSAKey.generate(2048))
        t.start_server(server=FakeSSH())
        chan = t.accept(20)
        if chan:
            chan.send("\r\n[Labyrinth AI Kernel Active]\r\n$ ")
            while True:
                data = chan.recv(1024).decode().strip()
                if not data: break
                resp, act = brain.process_command(data)
                brain.watcher_log(data, act)
                chan.send(f"\r\n{resp}\r\n$ ")
    except: pass

def start_backend():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 2222))
    sock.listen(10)
    print("[*] SSH Server is LIVE on Port 2222")
    while True:
        c, a = sock.accept()
        threading.Thread(target=handle_ssh, args=(c,)).start()

if __name__ == "__main__":
    start_backend()