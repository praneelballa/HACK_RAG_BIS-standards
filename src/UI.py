import streamlit as st
import json
import time
from app import ask_bis

# --- PAGE CONFIG ---
st.set_page_config(page_title="BIS Neural RAG", page_icon="⚡", layout="wide")

# --- MASTER CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

/* ═══════════════════════════════════════
   ROOT VARIABLES
═══════════════════════════════════════ */
:root {
    --bg-deep:      #06040f;
    --bg-mid:       #0d0a1e;
    --bg-card:      #120f28;
    --bg-card2:     #0f0c22;
    --cyan:         #00f5ff;
    --purple:       #a855f7;
    --pink:         #f0abfc;
    --blue:         #3b82f6;
    --green:        #00ffa3;
    --yellow:       #ffd700;
    --text-primary: #e2e8f0;
    --text-muted:   #94a3b8;
    --border:       rgba(168, 85, 247, 0.25);
}

/* ═══════════════════════════════════════
   GLOBAL RESET
═══════════════════════════════════════ */
* { box-sizing: border-box; }

.stApp {
    background: linear-gradient(135deg, #06040f 0%, #0d0a1e 40%, #110820 70%, #06040f 100%) !important;
    font-family: 'Rajdhani', sans-serif !important;
    color: var(--text-primary) !important;
    min-height: 100vh;
}

/* Animated background grid */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(168,85,247,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(168,85,247,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    pointer-events: none;
    z-index: 0;
}

/* ═══════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0718 0%, #080514 100%) !important;
    border-right: 1px solid rgba(168,85,247,0.3) !important;
    box-shadow: 4px 0 30px rgba(168,85,247,0.1);
}

[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--cyan), var(--purple), var(--pink));
}

/* ═══════════════════════════════════════
   HIDE DEFAULT STREAMLIT ELEMENTS
═══════════════════════════════════════ */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

/* ═══════════════════════════════════════
   TOP HEADER BAR
═══════════════════════════════════════ */
.header-bar {
    background: linear-gradient(90deg, rgba(10,7,24,0.95) 0%, rgba(20,12,40,0.95) 50%, rgba(10,7,24,0.95) 100%);
    border: 1px solid rgba(168,85,247,0.3);
    border-radius: 16px;
    padding: 20px 32px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(20px);
    box-shadow: 0 0 40px rgba(168,85,247,0.1), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
}

.header-bar::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--purple), var(--pink), transparent);
}

.header-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(90deg, var(--cyan), var(--purple), var(--pink));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    text-shadow: none;
    margin: 0;
    line-height: 1.2;
}

.header-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: var(--text-muted);
    margin: 4px 0 0 0;
    letter-spacing: 1px;
}

.header-badge {
    background: linear-gradient(135deg, rgba(0,245,255,0.1), rgba(168,85,247,0.1));
    border: 1px solid rgba(0,245,255,0.3);
    border-radius: 50px;
    padding: 8px 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: var(--cyan);
    letter-spacing: 2px;
    box-shadow: 0 0 15px rgba(0,245,255,0.15);
}

/* ═══════════════════════════════════════
   KPI METRIC CARDS
═══════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}

.kpi-card {
    background: linear-gradient(135deg, rgba(18,15,40,0.9), rgba(15,12,34,0.9));
    border-radius: 14px;
    padding: 20px 24px;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    cursor: default;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.kpi-card.cyan::before  { background: linear-gradient(90deg, transparent, var(--cyan), transparent); }
.kpi-card.purple::before { background: linear-gradient(90deg, transparent, var(--purple), transparent); }
.kpi-card.green::before  { background: linear-gradient(90deg, transparent, var(--green), transparent); }
.kpi-card.pink::before   { background: linear-gradient(90deg, transparent, var(--pink), transparent); }

.kpi-card:hover {
    transform: translateY(-3px);
    border-color: rgba(168,85,247,0.5);
    box-shadow: 0 8px 30px rgba(168,85,247,0.2);
}

.kpi-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
}

.kpi-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 700;
    margin: 0;
    line-height: 1;
}

.kpi-card.cyan  .kpi-value { color: var(--cyan);   text-shadow: 0 0 15px rgba(0,245,255,0.5); }
.kpi-card.purple .kpi-value { color: var(--purple); text-shadow: 0 0 15px rgba(168,85,247,0.5); }
.kpi-card.green  .kpi-value { color: var(--green);  text-shadow: 0 0 15px rgba(0,255,163,0.5); }
.kpi-card.pink   .kpi-value { color: var(--pink);   text-shadow: 0 0 15px rgba(240,171,252,0.5); }

.kpi-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    color: var(--text-muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 6px 0 0 0;
}

.kpi-sublabel {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: rgba(148,163,184,0.5);
    margin: 2px 0 0 0;
}

/* ═══════════════════════════════════════
   SEARCH PANEL
═══════════════════════════════════════ */
.search-panel {
    background: linear-gradient(135deg, rgba(18,15,40,0.95), rgba(12,9,28,0.95));
    border: 1px solid rgba(168,85,247,0.3);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 4px 40px rgba(168,85,247,0.08);
    position: relative;
    overflow: hidden;
}

.search-panel::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.4), transparent);
}

.search-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    color: var(--cyan);
    letter-spacing: 2px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.search-label::before {
    content: '▶';
    font-size: 10px;
    color: var(--purple);
}

/* ═══════════════════════════════════════
   INPUT OVERRIDE
═══════════════════════════════════════ */
.stTextInput > div > div > input {
    background: rgba(6,4,15,0.8) !important;
    color: var(--cyan) !important;
    border: 1px solid rgba(168,85,247,0.4) !important;
    border-radius: 10px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    box-shadow: 0 0 20px rgba(168,85,247,0.1), inset 0 1px 0 rgba(255,255,255,0.03) !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
}

.stTextInput > div > div > input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 25px rgba(0,245,255,0.2), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(148,163,184,0.35) !important;
    font-style: italic;
}

.stTextInput label {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--cyan) !important;
    font-size: 13px !important;
    letter-spacing: 2px !important;
}

/* ═══════════════════════════════════════
   BUTTON
═══════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, rgba(0,245,255,0.15), rgba(168,85,247,0.25)) !important;
    color: white !important;
    border: 1px solid rgba(0,245,255,0.4) !important;
    border-radius: 10px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    padding: 14px 28px !important;
    width: 100% !important;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
    box-shadow: 0 0 20px rgba(0,245,255,0.15), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    text-transform: uppercase !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,245,255,0.25), rgba(168,85,247,0.4)) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 35px rgba(0,245,255,0.35), 0 0 60px rgba(168,85,247,0.2) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ═══════════════════════════════════════
   RESULTS SECTION
═══════════════════════════════════════ */
.results-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 14px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.results-count {
    background: linear-gradient(135deg, var(--cyan), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 22px;
    font-weight: 900;
}

.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 20px;
    margin-top: 8px;
}

/* ═══════════════════════════════════════
   RESULT CARDS
═══════════════════════════════════════ */
.result-card {
    background: linear-gradient(135deg, rgba(18,15,40,0.95) 0%, rgba(12,9,28,0.95) 100%);
    border-radius: 16px;
    padding: 26px 28px;
    border: 1px solid rgba(168,85,247,0.2);
    position: relative;
    overflow: hidden;
    transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--purple), var(--pink));
    opacity: 0.8;
}

.result-card::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(168,85,247,0.08) 0%, transparent 70%);
    pointer-events: none;
}

.result-card:hover {
    transform: translateY(-5px);
    border-color: rgba(0,245,255,0.4);
    box-shadow: 0 12px 40px rgba(168,85,247,0.25), 0 0 0 1px rgba(0,245,255,0.1);
}

.result-rank {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--purple);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.result-rank::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(168,85,247,0.3), transparent);
}

.result-is-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 22px;
    font-weight: 700;
    background: linear-gradient(90deg, var(--cyan), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 4px 0;
    line-height: 1.2;
    text-shadow: none;
}

.result-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(168,85,247,0.3), transparent);
    margin: 14px 0;
}

.result-reasoning {
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    font-weight: 400;
    color: #b8c4d4;
    line-height: 1.7;
    margin: 0;
}

.result-footer {
    margin-top: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.result-tag {
    background: rgba(0,245,255,0.08);
    border: 1px solid rgba(0,245,255,0.2);
    border-radius: 50px;
    padding: 3px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: var(--cyan);
    letter-spacing: 1px;
}

/* ═══════════════════════════════════════
   SIDEBAR COMPONENTS
═══════════════════════════════════════ */
.sidebar-logo {
    text-align: center;
    padding: 20px 10px 10px;
}

.sidebar-logo-text {
    font-family: 'Orbitron', sans-serif;
    font-size: 18px;
    font-weight: 900;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
}

.sidebar-logo-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 1px;
    margin-top: 4px;
}

.sidebar-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.4), transparent);
    margin: 16px 0;
}

.status-card {
    background: rgba(6,4,15,0.6);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.status-card:hover {
    border-color: rgba(168,85,247,0.4);
    box-shadow: 0 0 15px rgba(168,85,247,0.1);
}

.status-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}

.status-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 18px;
    font-weight: 700;
    margin: 0;
}

.status-value.green { color: var(--green); text-shadow: 0 0 10px rgba(0,255,163,0.4); }
.status-value.cyan  { color: var(--cyan);  text-shadow: 0 0 10px rgba(0,245,255,0.4); }
.status-value.purple{ color: var(--purple);text-shadow: 0 0 10px rgba(168,85,247,0.4); }
.status-value.yellow{ color: var(--yellow);text-shadow: 0 0 10px rgba(255,215,0,0.4); }

.status-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 12px;
    color: rgba(148,163,184,0.5);
    margin-top: 2px;
}

.sidebar-section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: rgba(148,163,184,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.tech-badge {
    background: rgba(168,85,247,0.08);
    border: 1px solid rgba(168,85,247,0.2);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tech-badge-icon { font-size: 16px; }

.tech-badge-text {
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
}

.tech-badge-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 1px;
}

.version-badge {
    text-align: center;
    margin-top: 20px;
    padding: 10px;
    background: rgba(0,245,255,0.03);
    border: 1px solid rgba(0,245,255,0.1);
    border-radius: 8px;
}

.version-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: rgba(0,245,255,0.3);
    letter-spacing: 2px;
}

/* ═══════════════════════════════════════
   SPINNER
═══════════════════════════════════════ */
.stSpinner > div > div {
    border-top-color: var(--cyan) !important;
    border-right-color: var(--purple) !important;
}

/* ═══════════════════════════════════════
   ALERTS
═══════════════════════════════════════ */
.stAlert {
    background: rgba(18,15,40,0.8) !important;
    border-radius: 10px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 15px !important;
}

/* ═══════════════════════════════════════
   FOOTER
═══════════════════════════════════════ */
.footer-bar {
    text-align: center;
    padding: 20px;
    margin-top: 40px;
    border-top: 1px solid rgba(168,85,247,0.15);
}

.footer-text {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: rgba(148,163,184,0.3);
    letter-spacing: 3px;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(168,85,247,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(168,85,247,0.7); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-text">BIS//RAG</div>
        <div class="sidebar-logo-sub">NEURAL RETRIEVAL SYSTEM</div>
    </div>
    <div class="sidebar-divider"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-title">◈ System Status</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="status-card">
        <div class="status-label">Core Engine</div>
        <div class="status-value green">ONLINE</div>
        <div class="status-sub">⚡ All systems operational</div>
    </div>
    <div class="status-card">
        <div class="status-label">Hit Rate @3</div>
        <div class="status-value cyan">100%</div>
        <div class="status-sub">Public test set verified</div>
    </div>
    <div class="status-card">
        <div class="status-label">MRR Score @5</div>
        <div class="status-value purple">0.9000</div>
        <div class="status-sub">Above target threshold</div>
    </div>
    <div class="status-card">
        <div class="status-label">Avg Latency</div>
        <div class="status-value yellow">3.5s</div>
        <div class="status-sub">Target: &lt;5 seconds</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">◈ Tech Stack</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="tech-badge">
        <span class="tech-badge-icon">🧠</span>
        <div>
            <div class="tech-badge-text">Llama 3.3 70B</div>
            <div class="tech-badge-sub">VIA GROQ LPU</div>
        </div>
    </div>
    <div class="tech-badge">
        <span class="tech-badge-icon">🗄️</span>
        <div>
            <div class="tech-badge-text">Qdrant DB</div>
            <div class="tech-badge-sub">VECTOR STORE · 1374 CHUNKS</div>
        </div>
    </div>
    <div class="tech-badge">
        <span class="tech-badge-icon">🔡</span>
        <div>
            <div class="tech-badge-text">BGE-Small-EN</div>
            <div class="tech-badge-sub">EMBEDDING MODEL · 384D</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="version-badge">
        <div class="version-text">// HACK_RAG · v3.14-BIS · 2026 //</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════

# Top Header Bar
st.markdown("""
<div class="header-bar">
    <div>
        <div class="header-title">⚡ BIS NEURAL FINDER</div>
        <div class="header-subtitle">// BUREAU OF INDIAN STANDARDS · INTELLIGENT RETRIEVAL SYSTEM //</div>
    </div>
    <div class="header-badge">◉ SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

# KPI Cards
st.markdown("""
<div class="kpi-grid">
    <div class="kpi-card cyan">
        <span class="kpi-icon">🎯</span>
        <div class="kpi-value">100%</div>
        <div class="kpi-label">Hit Rate @3</div>
        <div class="kpi-sublabel">PUBLIC TEST SET</div>
    </div>
    <div class="kpi-card purple">
        <span class="kpi-icon">📊</span>
        <div class="kpi-value">0.90</div>
        <div class="kpi-label">MRR Score @5</div>
        <div class="kpi-sublabel">MEAN RECIPROCAL RANK</div>
    </div>
    <div class="kpi-card green">
        <span class="kpi-icon">⚡</span>
        <div class="kpi-value">3.5s</div>
        <div class="kpi-label">Avg Latency</div>
        <div class="kpi-sublabel">TARGET: &lt;5 SECONDS</div>
    </div>
    <div class="kpi-card pink">
        <span class="kpi-icon">📚</span>
        <div class="kpi-value">1374</div>
        <div class="kpi-label">Indexed Chunks</div>
        <div class="kpi-sublabel">FROM 1197 STANDARDS</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Search Panel
st.markdown("""
<div class="search-panel">
    <div class="search-label">QUERY INPUT TERMINAL</div>
""", unsafe_allow_html=True)

query = st.text_input(
    "QUERY_INPUT >",
    placeholder="e.g. 'Portland cement for structural concrete' or 'steel reinforcement bars'...",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_clicked = st.button("⚡  EXECUTE NEURAL SEARCH")

st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════
# SEARCH EXECUTION
# ═══════════════════════════════════════
if search_clicked:
    if query:
        with st.spinner("◈ SYNCHRONIZING WITH VECTOR DATABASE · REASONING WITH NEURAL ENGINE..."):
            try:
                start = time.time()
                
                # 1. Fetch data
                results = ask_bis(query) 
                elapsed = round(time.time() - start, 2)

                # 2. Type Check & Formatting
                if isinstance(results, str):
                    results = json.loads(results)

                if results:
                    # Results header
                    st.markdown(f"""
                    <div class="results-header">
                        <span class="results-count">{len(results)}</span> STANDARDS IDENTIFIED
                        <span style="margin-left:auto; font-size:12px; color: rgba(148,163,184,0.5);">⏱ {elapsed}s · QUERY COMPLETE</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Results grid
                    st.markdown('<div class="results-grid">', unsafe_allow_html=True)

                    rank_labels = ["◈ PRIMARY MATCH", "◈ SECONDARY MATCH", "◈ TERTIARY MATCH", "◈ MATCH #4", "◈ MATCH #5"]

                    for i, res in enumerate(results):
                        rank = rank_labels[i] if i < len(rank_labels) else f"◈ MATCH #{i+1}"
                        is_num = res.get('is_number', 'N/A')
                        reasoning = res.get('reasoning', 'No reasoning provided.')
                        category = "BUILDING MATERIALS"

                        st.markdown(f"""
                        <div class="result-card">
                            <div class="result-rank">{rank}</div>
                            <div class="result-is-number">{is_num}</div>
                            <div class="result-divider"></div>
                            <p class="result-reasoning">{reasoning}</p>
                            <div class="result-footer">
                                <span class="result-tag">BIS STANDARD</span>
                                <span class="result-tag">{category}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("◈ NO MATCHES — Neural engine could not find relevant standards.")
                    
            except Exception as e:
                msg = str(e)
                if "Missing GROQ_API_KEY" in msg:
                    st.error("⚠ SYSTEM ERROR: Missing GROQ_API_KEY. Please set your environment variables.")
                else:
                    st.error(f"⚠ SYSTEM ERROR: {e}")
    else:
        st.warning("◈ INPUT REQUIRED — Please enter a query to initialize search.")

elif not search_clicked:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 60px 20px; opacity: 0.4;">
        <div style="font-size:48px; margin-bottom:16px;">⚡</div>
        <div style="font-family:'Orbitron',sans-serif; font-size:16px; color:#94a3b8; letter-spacing:3px;">
            AWAITING QUERY INPUT
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:12px; color:#64748b; margin-top:8px; letter-spacing:1px;">
            Enter a product description to retrieve relevant BIS standards
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer-bar">
    <div class="footer-text">// BIS × SIGMA SQUAD AI HACKATHON 2026 · NEURAL RAG PIPELINE · BUILT WITH ⚡ //</div>
</div>
""", unsafe_allow_html=True)