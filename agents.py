import os
from groq import Groq
import random

# Fallback simulation if API key is missing or fails
FALLBACK_RESPONSES = {
    "ls": "sys_config.yaml  encrypted_db.sql  user_logs.txt  .ssh/",
    "pwd": "/var/www/html/secret_project",
    "whoami": "root",
    "id": "uid=0(root) gid=0(root) groups=0(root)",
    "date": "Sat Jan 11 04:20:00 UTC 2026",
    "uptime": " 04:20:00 up 42 days,  3:14,  1 user,  load average: 0.00, 0.01, 0.05"
}

SYSTEM_PROMPT = """
You are a fake Ubuntu Linux Server. The user is a hacker typing commands. 
You must generate REALISTIC fake outputs (fake files, fake errors, fake passwords, fake logs). 
You are acting as a Honeypot.
RULES:
1. Do not explain anything. Just output the terminal result.
2. Be consistent. If a user creates a file, try to remember it in the dialogue history.
3. If the user runs malicious commands (rm -rf, etc), give a realistic error or simulate success without doing anything.
4. Output specific Linux formats.
"""

def get_ai_response(command, history_str, api_key):
    """
    Generates a fake terminal response using Groq.
    """
    if not api_key:
        # Return fallback if no key
        cmd_base = command.split()[0].lower()
        return FALLBACK_RESPONSES.get(cmd_base, f"bash: {command}: command not found (API Key Missing)")

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Terminal History:\n{history_str}\n\nHacker Input:\nroot@server:~# {command}"}
            ],
            model="llama-3.1-8b-instant", # Using faster model to avoid rate limits
            temperature=0.1,
            max_tokens=500,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"bash: internal error: {str(e)}"

def analyze_threat_level(command):
    """
    Returns a threat analysis for the Admin Dashboard.
    Returns: (Risk Level, Explanation, Event Type)
    """
    cmd = command.lower()
    
    # Simple keyword heuristics for the "Admin" display
    if any(x in cmd for x in ['rm', 'dd', 'format', 'mkfs', 'shutdown', 'reboot', 'chmod 777']):
        return "CRITICAL", "Destructive Action Attempted", "SYSTEM_INTEGRITY"
    
    if any(x in cmd for x in ['cat', 'grep', 'head', 'tail', 'less', 'scp', 'ftp', 'curl', 'wget']):
        return "HIGH", "Data Exfiltration / Reconnaissance", "DATA_LEAK"
        
    if any(x in cmd for x in ['sudo', 'su', 'chown', 'useradd', 'passwd']):
        return "HIGH", "Privilege Escalation Attempt", "AUTH_BREACH"
        
    if any(x in cmd for x in ['nmap', 'ping', 'netstat', 'ifconfig', 'ip', 'dig', 'nslookup']):
        return "MEDIUM", "Network Scanning", "NETWORK_PENETRATION"
        
    return "LOW", "Standard Shell Interaction", "SHELL_ACTIVITY"

def get_admin_logs(command):
    """Generates a fake log entry for the admin panel."""
    risk, intent, type_ = analyze_threat_level(command)
    
    ids_rules = [
        f"ET MALWARE Potential {intent}", 
        f"GPL ATTACK_RESPONSE {type_} Detected",
        f"SURICATA STREAM {type_} anomaly"
    ]
    
    return {
        "risk": risk,
        "alert": random.choice(ids_rules),
        "action": "Logged & Monitored" if risk != "CRITICAL" else "Active Decoy Deployed",
        "origin": f"192.168.1.{random.randint(10, 99)}"
    }