import streamlit as st
import os
import pandas as pd
import numpy as np
import pydeck as pdk
import time
from datetime import datetime
from dotenv import load_dotenv
from agents import get_ai_response, analyze_threat_level, get_admin_logs

# Load environment variables
load_dotenv()

# --- CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="GhostShell: v3.0 SOC",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if "history" not in st.session_state:
    st.session_state.history = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "packets" not in st.session_state:
    # Fake packet data for the "Deep Packet Inspection" table
    st.session_state.packets = pd.DataFrame(columns=["Timestamp", "Source IP", "Protocol", "Payload", "Flag"])

# --- CUSTOM CSS (ANIMATIONS & CYBERPUNK THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* BASE STYLES */
    .stApp {
        background-color: #020202;
        color: #00FF41;
        font-family: 'Share Tech Mono', monospace;
    }
    
    /* ANIMATIONS */
    @keyframes scanline {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100vh); }
    }
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0.7); }
        70% { box-shadow: 0 0 10px 10px rgba(255, 0, 85, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 85, 0); }
    }
    @keyframes glitch {
        0% { text-shadow: 2px 2px #FF0055; }
        25% { text-shadow: -2px -2px #00FF41; }
        50% { text-shadow: 2px -2px #FF0055; }
        75% { text-shadow: -2px 2px #00FF41; }
        100% { text-shadow: 2px 2px #FF0055; }
    }

    /* CLASSES */
    .scanline-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100vh;
        background: linear-gradient(to bottom, transparent, rgba(0, 255, 65, 0.1), transparent);
        animation: scanline 4s linear infinite;
        pointer-events: none;
        z-index: 999;
    }
    
    .critical-alert {
        animation: pulse-red 2s infinite;
        border: 2px solid #FF0055 !important;
    }
    
    .glitch-text {
        animation: glitch 1s infinite;
        font-size: 3em !important;
        color: white !important;
        text-align: center;
        border-bottom: 2px solid #00FF41;
        margin-bottom: 20px;
    }
    
    /* COMPONENTS */
    .stTextInput input {
        background-color: #0a0a0a !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8em !important;
        color: #00FF41 !important;
    }
    
    /* CUSTOM CONTAINERS */
    .cyber-card {
        background-color: #050505;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
<div class="scanline-overlay"></div>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1 class='glitch-text'>👻 GhostShell v3.0 // ACTIVE DEFENSE</h1>", unsafe_allow_html=True)

# --- SECTION 1: MAIN CONFLICT (SPLIT SCREEN) ---
col_hacker, _, col_admin = st.columns([1, 0.05, 1.2])

with col_hacker:
    st.markdown("### 💀 TERMINAL INTERFACE_")
    terminal = st.container(height=500, border=True)
    with terminal:
        for cmd, out in st.session_state.history[-10:]:
            st.markdown(f"> `root@ghostshell:~# {cmd}`")
            st.code(out, language="bash")
    
    command = st.text_input("root@ghostshell:~#", key="cmd_input")
    
    if command:
        api_key = os.getenv("GROQ_API_KEY")
        # Generate Log
        log = get_admin_logs(command)
        log['timestamp'] = datetime.now().strftime("%H:%M:%S")
        log['command'] = command
        st.session_state.logs.insert(0, log)
        
        # Generate Response
        resp = get_ai_response(command, str(st.session_state.history[-3:]), api_key)
        st.session_state.history.append((command, resp))
        
        # Fake Packet Data Generation
        new_packet = {
            "Timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "Source IP": "192.168.45.21", 
            "Protocol": "SSH" if "ssh" in command else "TCP",
            "Payload": f"LEN={len(command)*8}bits",
            "Flag": "PSH, ACK"
        }
        st.session_state.packets = pd.concat([pd.DataFrame([new_packet]), st.session_state.packets], ignore_index=True).head(50)
        
        st.rerun()

with col_admin:
    st.markdown("### 🛡️ SOC MONITOR_")
    
    # Live Threat Metrics
    m1, m2, m3, m4 = st.columns(4)
    risk = st.session_state.logs[0]['risk'] if st.session_state.logs else "LOW"
    
    m1.metric("DEFCON", "4" if risk == "LOW" else "1", delta_color="inverse")
    m2.metric("Threat", risk)
    m3.metric("Uptime", "99.9%")
    m4.metric("Decoys", "24/24")

    # Map
    st.markdown("#### 🌍 GEO-THREAD ORIGIN")
    map_data = pd.DataFrame(
        np.random.randn(20, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon'])
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v9",
        initial_view_state=pdk.ViewState(latitude=37.76, longitude=-122.4, zoom=3, pitch=40),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                map_data,
                get_position='[lon, lat]',
                get_color='[0, 255, 65, 100]',
                get_radius=200000,
            ),
             pdk.Layer(
                "ArcLayer",
                data=pd.DataFrame([{
                    "source": [-122.4194, 37.7749], 
                    "target": [77.2090, 28.6139]
                }]),
                get_source_position="source",
                get_target_position="target",
                get_source_color=[0, 255, 65],
                get_target_color=[255, 0, 85],
                get_width=5,
            )
        ],
    ))

# --- SECTION 2: DEEP PACKET INSPECTION (THE "LONG" PART) ---
st.markdown("---")
st.markdown("### � DEEP PACKET INSPECTION (DPI)")

dpi_col1, dpi_col2 = st.columns([2, 1])

with dpi_col1:
    st.dataframe(
        st.session_state.packets, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "Timestamp": "TIME",
            "Source IP": "SRC",
            "Protocol": "PROTO",
            "Payload": "SIZE"
        }
    )

with dpi_col2:
    st.markdown("#### 📊 TRAFFIC ANOMALIES")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["HTTP", "SSH", "FTP"])
    st.area_chart(chart_data, color=["#00FF41", "#008F11", "#004400"])

# --- SECTION 3: SYSTEM RESOURCES ---
st.markdown("---")
st.markdown("### 🖥️ NODE STATUS")

r1, r2, r3 = st.columns(3)
with r1:
    st.markdown("**CPU LOAD**")
    st.progress(0.45)
    st.caption("Core 0-12: OPTIMAL")
    
with r2:
    st.markdown("**MEMORY INTEGRITY**")
    st.progress(0.92)
    st.caption("ECC Checks: PASSED")

with r3:
    st.markdown("**DECOY SATURATION**")
    st.progress(0.15)
    st.caption("Deployed: 402 / 5000")

# --- FOOTER ---
st.markdown("<center style='color: #333;'>GHOSTSHELL ACTIVE DEFENSE V3.0 // DEVELOPED BY ANTIGRAVITY AGENT</center>", unsafe_allow_html=True)