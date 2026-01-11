import streamlit as st
import pandas as pd
import datetime
from agents import get_ai_response, analyze_threat

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GhostShell: Active Defense",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= CUSTOM CSS (From appli.py) =================
st.markdown("""
<style>
    /* MAIN THEME */
    .stApp { background-color: #050505; color: #00FF41; }
    
    /* NEON TITLES */
    .neon-text {
        font-size: 50px;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
        margin-bottom: 10px;
    }
    
    /* CARD DESIGN */
    .agent-card {
        background: radial-gradient(circle at top, #0b2c3a, #000000);
        border: 1px solid #333;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 198, 255, 0.1);
        transition: transform 0.3s;
    }
    .agent-card:hover { transform: scale(1.05); border-color: #00c6ff; }
    .agent-title { font-size: 20px; font-weight: bold; color: #fff; }
    .agent-status { font-size: 14px; color: #00FF41; margin-top: 5px; }

    /* TERMINAL STYLING */
    .terminal-window {
        background-color: #0d0d0d;
        border: 1px solid #00FF41;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        height: 450px;
        overflow-y: auto;
        box-shadow: inset 0 0 20px rgba(0, 255, 65, 0.1);
    }
    .cmd-text { color: #00FF41; }
    .output-text { color: #c0c0c0; margin-bottom: 10px; white-space: pre-wrap; }

    /* INPUT FIELD OVERRIDE */
    .stTextInput input {
        background-color: #111 !important;
        color: #00FF41 !important;
        border: 1px solid #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE INIT =================
if "terminal_history" not in st.session_state:
    st.session_state.terminal_history = []  # Stores {cmd, output}
if "logs" not in st.session_state:
    st.session_state.logs = []
if "threat_level" not in st.session_state:
    st.session_state.threat_level = "SAFE"

# ================= HEADER =================
st.markdown('<p class="neon-text">👻 GHOSTSHELL: DECEPTION ENGINE</p>', unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #888; margin-bottom: 30px;'>Autonomous AI Honeypot • Multi-Agent Defense • Live Threat Tracking</div>", unsafe_allow_html=True)

# ================= API KEY INPUT (Sidebar) =================
with st.sidebar:
    st.header("⚙️ System Config")
    api_key = st.text_input("Groq API Key (Optional)", type="password", placeholder="gsk_...")
    if st.button("Clear Logs"):
        st.session_state.logs = []
        st.session_state.terminal_history = []
        st.rerun()

# ================= 4 AGENT CARDS =================
c1, c2, c3, c4 = st.columns(4)

# Calculate Active Agents based on logs
last_agent = st.session_state.logs[-1]["agent"] if st.session_state.logs else "Idle"

def render_card(col, icon, name, desc, is_active):
    border = "2px solid #00FF41" if is_active else "1px solid #333"
    glow = "box-shadow: 0 0 20px rgba(0,255,65,0.4);" if is_active else ""
    col.markdown(f"""
    <div class="agent-card" style="border: {border}; {glow}">
        <div style="font-size: 30px;">{icon}</div>
        <div class="agent-title">{name}</div>
        <div style="color: #888; font-size: 12px;">{desc}</div>
        <div class="agent-status">{'● ACTIVE' if is_active else '○ STANDBY'}</div>
    </div>
    """, unsafe_allow_html=True)

render_card(c1, "👁️", "Watchman", "Intrusion Detection", last_agent == "Watchman")
render_card(c2, "🏗️", "Architect", "Illusion Builder", last_agent == "Architect")
render_card(c3, "🎭", "Mimic", "Behavior Emulator", last_agent == "Mimic")
render_card(c4, "🏹", "Hunter", "Threat Intelligence", last_agent == "Hunter")

st.write("---")

# ================= MAIN INTERFACE (Split View) =================
col_term, col_dash = st.columns([1.5, 1])

# --- LEFT: TERMINAL (The Trap) ---
with col_term:
    st.subheader("🖥️ Attacker Terminal (Sandboxed)")
    
    # Render Terminal Window
    terminal_content = ""
    for entry in st.session_state.terminal_history:
        terminal_content += f"<div class='cmd-text'>root@ghostshell:~# {entry['cmd']}</div>"
        terminal_content += f"<div class='output-text'>{entry['output']}</div>"
    
    st.markdown(f"""
    <div class="terminal-window">
        <div style="color: #555;">Linux 5.4.0-42-generic (Ubuntu) | System Time: {datetime.datetime.now().strftime('%H:%M:%S')}</div>
        <br>
        {terminal_content}
        <div id="anchor"></div>
    </div>
    """, unsafe_allow_html=True)

    # Command Input
    with st.form("cmd_form", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        user_input = col_in.text_input("Input", placeholder="Type a command (ls, whoami, cat...)", label_visibility="collapsed")
        submitted = col_btn.form_submit_button("RUN")
        
        if submitted and user_input:
            # 1. Analyze Threat
            threat, agent, thought = analyze_threat(user_input)
            
            # 2. Get AI Response
            ai_reply = get_ai_response(
                user_input, 
                str([x['cmd'] for x in st.session_state.terminal_history]), 
                api_key
            )
            
            # 3. Update State
            st.session_state.terminal_history.append({"cmd": user_input, "output": ai_reply})
            st.session_state.logs.append({
                "Time": datetime.datetime.now().strftime('%H:%M:%S'),
                "Command": user_input,
                "Agent": agent,
                "Threat": threat,
                "Analysis": thought
            })
            st.session_state.threat_level = threat
            st.rerun()

# --- RIGHT: DEFENDER DASHBOARD ---
with col_dash:
    st.subheader("🛡️ Defender Intelligence")
    
    # Threat Monitor
    curr_threat = st.session_state.threat_level
    color = "red" if curr_threat == "CRITICAL" else "orange" if curr_threat == "HIGH" else "#00FF41"
    st.markdown(f"""
    <div style="background: #111; padding: 15px; border-radius: 10px; border-left: 5px solid {color}; margin-bottom: 20px;">
        <h3 style="margin:0; color:{color};">THREAT LEVEL: {curr_threat}</h3>
        <p style="margin:0; color:#fff;">Live Origin: 45.112.90.11 (Moscow, RU)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Live Logs
    st.write("#### 📝 Agent Thought Logs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        
        # Stylized Dataframe
        st.dataframe(
            df[["Time", "Agent", "Command", "Threat"]].iloc[::-1], # Reverse order
            hide_index=True,
            use_container_width=True,
            height=300
        )
        
        # Show latest thought
        last_log = st.session_state.logs[-1]
        st.info(f"🧠 **{last_log['Agent']} Reasoning:** {last_log['Analysis']}")
    else:
        st.write("Waiting for intrusion...")

# ================= FOOTER =================
st.markdown("---")
st.markdown("<center style='color: #444;'>GhostShell AI v3.0 | Created by Merging Best Hackathon Modules</center>", unsafe_allow_html=True)import streamlit as st
import datetime
import pandas as pd
from agents import get_ai_response, analyze_threat

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="GhostShell AI",
    page_icon="👻",
    layout="wide"
)

# ================= CSS (EXACTLY FROM APPLI.PY) =================
st.markdown("""
<style>
/* MAIN TITLE STYLE */
.main-title {
    font-size:96px !important;   
    font-weight:900;
    color:#ffffff;
    text-align:center;
    letter-spacing:4px;
    margin-top:20px;
    margin-bottom:10px;
    text-shadow: 0 0 20px rgba(0,198,255,0.6);
}
.sub-title {
    font-size:20px;
    color:#9aa6ac;
    text-align:center;
    margin-top:25px;      
    line-height:1.8;      
}

/* 3D FLIP CARDS */
.card {
    position: relative;
    padding: 25px;
    border-radius: 18px;
    background: radial-gradient(circle at top, #0b2c3a, #050b10);
    box-shadow: 0 0 22px rgba(0,198,255,0.35);
    height: 190px;
    overflow: hidden;
    transition: all 0.4s ease;
}
.card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 0 45px rgba(0,198,255,0.7);
}
.card .front {
    position: relative;
    z-index: 2;
    transition: opacity 0.3s ease, transform 0.3s ease;
}
.card .front h4 { margin-top: 12px; font-size: 22px; color: #ffffff; }
.card .front p { color: #9adfff; font-size: 14px; }
.card:hover .front { opacity: 0; transform: translateY(-15px); }

/* HOVER CONTENT */
.card .hover-content {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(0, 20, 30, 0.97), rgba(0, 5, 10, 0.98));
    backdrop-filter: blur(8px);
    padding: 28px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
    opacity: 0;
    transform: translateY(25px);
    transition: all 0.4s ease;
}
.card:hover .hover-content { opacity: 1; transform: translateY(0); }
.hover-title { font-size: 22px; font-weight: 700; color: #00c6ff; margin-bottom: 8px; }
.hover-sub { font-size: 13px; letter-spacing: 1px; color: #7fdcff; margin-bottom: 10px; text-transform: uppercase; }
.hover-desc { font-size: 14px; color: #d4e9f2; line-height: 1.6; }

/* TERMINAL & LOGS */
.terminal { background:black; color:#00ff9c; padding:15px; border-radius:10px; font-family:monospace; margin-top: 10px; white-space: pre-wrap; }
.agent-log { background:#0e161b; padding:10px; border-left:4px solid #00c6ff; margin-bottom:6px; font-family:monospace; color:#cbefff; }
.stTextInput input { background-color: #0e161b !important; color: #00c6ff !important; border: 1px solid #00c6ff !important; }
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "terminal_history" not in st.session_state:
    st.session_state.terminal_history = "System Initialized... Waiting for input..."
if "logs" not in st.session_state:
    st.session_state.logs = []
if "agent_logs" not in st.session_state:
    st.session_state.agent_logs = []
if "illusion_level" not in st.session_state:
    st.session_state.illusion_level = 1

# ================= SIDEBAR (CONFIG) =================
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Groq API Key (Optional)", type="password")
    if st.button("🔴 RESET SYSTEM"):
        st.session_state.terminal_history = "System Reset..."
        st.session_state.logs = []
        st.session_state.agent_logs = []
        st.rerun()

# ================= HEADER =================
st.markdown("""
<div>
    <p class="main-title">👻 GhostShell AI</p>
    <p class="sub-title">Autonomous Cyber Deception System — Attackers enter illusions, not your real system</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ================= FEATURE CARDS (3D FLIP) =================
c1, c2, c3, c4 = st.columns(4)

# We use the EXACT HTML structure from appli.py
c1.markdown("""
<div class="card">
    <div class="front">🧍‍♂️<h4>Watchman</h4><p>Intrusion Detection</p></div>
    <div class="hover-content">
        <div class="hover-title">Watchman</div><div class="hover-sub">Intrusion Detection</div>
        <div class="hover-desc">Detects intrusion entry points and instantly activates deception environments.</div>
    </div>
</div>""", unsafe_allow_html=True)

c2.markdown("""
<div class="card">
    <div class="front">🏗️<h4>Architect</h4><p>Illusion Builder</p></div>
    <div class="hover-content">
        <div class="hover-title">Architect</div><div class="hover-sub">Deception Designer</div>
        <div class="hover-desc">Dynamically builds fake systems, files and paths that look real.</div>
    </div>
</div>""", unsafe_allow_html=True)

c3.markdown("""
<div class="card">
    <div class="front">🪞<h4>Mimic</h4><p>Reactive System</p></div>
    <div class="hover-content">
        <div class="hover-title">Mimic</div><div class="hover-sub">Behavior Emulator</div>
        <div class="hover-desc">Responds exactly like a compromised real system to maintain trust.</div>
    </div>
</div>""", unsafe_allow_html=True)

c4.markdown("""
<div class="card">
    <div class="front">🐺<h4>Hunter</h4><p>Silent Tracker</p></div>
    <div class="hover-content">
        <div class="hover-title">Hunter</div><div class="hover-sub">Threat Intelligence</div>
        <div class="hover-desc">Silently records attacker commands and builds behavioral intelligence.</div>
    </div>
</div>""", unsafe_allow_html=True)

st.divider()

# ================= ILLUSION ROOM (LIVE TERMINAL) =================
st.subheader("🪞 Illusion Room (Live Attacker Terminal)")

# Input for the "Hacker"
col_in, col_btn = st.columns([4, 1])
with col_in:
    command = st.text_input("Attacker Command Input", label_visibility="collapsed", placeholder="type command (ls, cat, sudo)...")
with col_btn:
    run_btn = st.button("EXECUTE 👻", type="primary")

if run_btn and command:
    # 1. Backend: Analyze Threat
    threat, agent, thought = analyze_threat(command)
    
    # 2. Backend: Get AI Response (Groq)
    ai_response = get_ai_response(command, st.session_state.terminal_history, api_key)
    
    # 3. Update State
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.illusion_level += 1
    
    # Append to Terminal
    st.session_state.terminal_history += f"\nroot@ghostshell:~# {command}\n{ai_response}"
    
    # Add to Logs
    st.session_state.logs.append({
        "Time": timestamp, "Command": command, "Agent": agent, "Threat": threat, "Level": st.session_state.illusion_level
    })
    
    # Add to Agent Chat
    st.session_state.agent_logs.append(f"[{timestamp}] [{agent}] {thought}")

# Display Terminal Output
st.markdown(f"<div class='terminal'>{st.session_state.terminal_history}</div>", unsafe_allow_html=True)

if len(st.session_state.logs) > 0:
    last_threat = st.session_state.logs[-1]["Threat"]
    if last_threat == "CRITICAL":
        st.warning("⚠️ CRITICAL THREAT: DECEPTION LEVEL MAXIMIZED")

st.divider()

# ================= INTELLIGENCE DASHBOARD =================
col_logs, col_agents = st.columns([1.5, 1])

with col_logs:
    st.subheader("🛡️ Defender Intelligence Logs")
    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df.iloc[::-1], use_container_width=True, height=300) # Show new logs on top
    else:
        st.info("System Secure. Waiting for intrusion...")

with col_agents:
    st.subheader("🧠 Internal Agent Communication")
    # Show last 5 agent thoughts
    for log in st.session_state.agent_logs[-5:]:
        st.markdown(f"<div class='agent-log'>{log}</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<center>© 2026 | GhostShell AI – Autonomous Cyber Deception System</center>", unsafe_allow_html=True)