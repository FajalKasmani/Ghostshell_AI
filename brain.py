import os
from datetime import datetime

class GhostBrain:
    def __init__(self):
        self.current_path = "/home/admin"
        self.log_file = "attacks.csv"

    def process_command(self, cmd):
        cmd = cmd.strip().lower()
        if cmd == "ls":
            return "secret_data.db  config.yaml  logs/", "Architect: Fake FS Generated"
        elif cmd == "whoami":
            return "root", "PuppetMaster: Privilege Escalation Spoofed"
        elif "cd" in cmd:
            return "", "Architect: Sandbox Path Updated"
        return f"bash: {cmd}: command not found", "Watcher: Command Logged"

    def watcher_log(self, command, action):
        now = datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{now},SSH,{command},{action}\n")