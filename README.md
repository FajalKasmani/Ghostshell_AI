GhostShell AI: Autonomous Multi-Agent Deception System
GhostShell AI is a next-generation cybersecurity platform designed to neutralize intruders through high-fidelity deception. Instead of just blocking attacks, it traps hackers in a simulated virtual environment (Labyrinth) and uses autonomous agents to manipulate their behavior and collect threat intelligence.

🚀 Key Features
Autonomous Agent Orchestration: Real-time decision-making by specialized agents.

High-Fidelity SSH Honeypot: A realistic terminal environment that lures hackers into an "infinite loop."

Live SOC Dashboard: Visualizes attack metrics, workload distribution, and agent "thought processes."

Behavioral Intelligence: Logs hacker commands and maps them to defensive logic.

🤖 Meet the Agents
Architect Agent: Manages the fake filesystem. It generates non-existent directories and files to keep the attacker busy.

Puppet Master Agent: Manipulates identity and permissions. It spoofs "root" access to trick attackers into revealing their tools.

Watcher Agent: The system's eyes. It monitors every command and updates the global threat dashboard.

🛠️ Installation & Setup
Prerequisites
Python 3.x

paramiko library (for the SSH engine)

Bash

pip install paramiko
Running the Project
Start the System:

Bash

python app.py
Access the Dashboard: Open your browser and go to http://localhost:5050.

Simulate an Attack: Open a new terminal and connect via SSH:

Bash

ssh root@127.0.0.1 -p 2222
📊 How to Demo
Initial State: Show the dashboard with 0 threats and empty workload charts.

Engagement: Connect via SSH and type ls. Show how the Architect Agent workload bar increases.

Privilege Trap: Type whoami. Show how the Puppet Master Agent responds with "root" and explains its logic on the dashboard.

Intelligence Feed: Point to the "Agent Reasoning Stream" where each card shows why the AI made a specific defensive choice.

📝 Description for Hackathon
"GhostShell AI is an autonomous multi-agent deception system that traps attackers within a simulated virtual environment to analyze their behavior. It utilizes specialized Architect and Puppet Master agents to manipulate and record every intruder movement in real-time, turning a security threat into a controlled intelligence-gathering session."
