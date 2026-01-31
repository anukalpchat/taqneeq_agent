"""
utils/styling.py
Injects the full SENTINEL dark-theme CSS into the Streamlit app.
"""
import streamlit as st


def inject_custom_css():
    css = """
    <style>
    /* ──────────────────────────────────────────────
       GOOGLE FONTS
       ────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

    /* ──────────────────────────────────────────────
       ROOT VARIABLES
       ────────────────────────────────────────────── */
    :root {
        --bg-deep:      #050e1a;
        --bg-base:      #0a1929;
        --bg-card:      #0f2238;
        --bg-card-hi:   #162d4a;
        --border:       #1e4976;
        --border-hi:    #2a6496;
        --text-primary: #e2e8f0;
        --text-dim:     #7a8fa6;
        --text-label:   #4e7a9e;
        --accent:       #00d4ff;
        --accent-dim:   #0099b8;
        --green:        #4caf50;
        --green-dim:    #2e7d32;
        --green-glow:   rgba(76,175,80,0.18);
        --amber:        #ffb74d;
        --amber-dim:    #e68900;
        --red:          #ef5350;
        --red-dim:      #c62828;
        --red-glow:     rgba(239,83,80,0.2);
        --terminal-bg:  #040a12;
        --terminal-fg:  #39ff85;
    }

    /* ──────────────────────────────────────────────
       GLOBAL / STREAMLIT OVERRIDES
       ────────────────────────────────────────────── */
    html, body {
        background: var(--bg-deep) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Kill Streamlit chrome */
    #MainMenu            { visibility: hidden !important; }
    footer               { visibility: hidden !important; }
    .stDeployButton      { display: none !important; }
    header               { display: none !important; }

    /* Full-bleed layout */
    .main .block-container {
        padding-top:    0.6rem !important;
        padding-bottom: 2rem   !important;
        padding-left:   1rem   !important;
        padding-right:  1rem   !important;
        max-width:      100%   !important;
    }

    /* Streamlit metric overrides */
    div[data-testid="metric-container"] {
        background: var(--bg-card);
        border:     1px solid var(--border);
        border-radius: 10px;
        padding:    0.8rem 1rem !important;
    }
    div[data-testid="metric-container"] div:first-child {
        color: var(--text-label) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div:nth-child(2) {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
    }

    /* Expander styling */
    .streamlit-expander {
        border: 1px solid var(--border) !important;
        background: var(--bg-card) !important;
        border-radius: 6px !important;
        margin-bottom: 0.4rem !important;
    }
    .streamlit-expander .streamlit-expander-title {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
    }

    /* Plotly chart backgrounds */
    .plotly .modebar { background: transparent !important; }

    /* ──────────────────────────────────────────────
       SENTINEL CUSTOM CLASSES
       ────────────────────────────────────────────── */

    /* ── HEADER BANNER ── */
    .sentinel-header {
        background:    linear-gradient(135deg, #0b1e35 0%, #0a1929 50%, #091525 100%);
        border-bottom: 1px solid var(--border);
        padding:       0.7rem 1.2rem;
        display:       flex;
        align-items:   center;
        justify-content: space-between;
        gap:           1rem;
        border-radius: 0 0 12px 12px;
        position:      relative;
        overflow:      hidden;
    }
    .sentinel-header::before {
        content:  '';
        position: absolute;
        top:      0; left: 0; right: 0;
        height:   2px;
        background: linear-gradient(90deg, transparent 0%, var(--accent) 30%, var(--accent) 70%, transparent 100%);
        opacity:  0.6;
    }
    .sentinel-header .logo-block {
        display:    flex;
        align-items: center;
        gap:        0.7rem;
        flex-shrink: 0;
    }
    .sentinel-header .logo-icon {
        font-size: 1.6rem;
        filter:    drop-shadow(0 0 6px rgba(0,212,255,0.5));
    }
    .sentinel-header .logo-text {
        font-family:    'Rajdhani', sans-serif;
        font-size:      1.5rem;
        font-weight:    700;
        color:          var(--accent);
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .sentinel-header .logo-sub {
        font-size:      0.62rem;
        color:          var(--text-label);
        letter-spacing: 0.22em;
        text-transform: uppercase;
        display:        block;
        margin-top:     -2px;
    }

    /* ── STATUS PULSE ── */
    .status-live {
        display:    flex;
        align-items: center;
        gap:        0.45rem;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        color:      var(--green);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .status-live .pulse-dot {
        width:  8px;
        height: 8px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 6px var(--green);
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--green); }
        50%      { opacity: 0.4; box-shadow: 0 0 2px var(--green); }
    }

    /* ── HERO PROFIT CARDS ── */
    .hero-profit-card {
        border-radius:  14px;
        padding:        1.1rem 1rem;
        text-align:     center;
        position:       relative;
        overflow:       hidden;
        min-height:     130px;
        display:        flex;
        flex-direction: column;
        align-items:    center;
        justify-content:center;
        border:         1px solid transparent;
    }
    .hero-profit-card .card-label {
        font-family:    'Rajdhani', sans-serif;
        font-size:      0.7rem;
        font-weight:    600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        margin-bottom:  0.25rem;
    }
    .hero-profit-card .card-value {
        font-family: 'Rajdhani', sans-serif;
        font-size:   2.6rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .hero-profit-card .card-sub {
        font-size:  0.68rem;
        margin-top: 0.3rem;
        opacity:    0.7;
    }

    .hero-card-loss {
        background: linear-gradient(145deg, rgba(239,83,80,0.12) 0%, rgba(198,40,40,0.06) 100%);
        border-color: rgba(239,83,80,0.25);
        color:      var(--red);
    }
    .hero-card-loss .card-label { color: var(--red); }
    .hero-card-loss .card-sub   { color: rgba(239,83,80,0.6); }

    .hero-card-profit {
        background: linear-gradient(145deg, rgba(76,175,80,0.14) 0%, rgba(46,125,50,0.06) 100%);
        border-color: rgba(76,175,80,0.3);
        color:       var(--green);
        box-shadow:  0 0 18px rgba(76,175,80,0.12);
    }
    .hero-card-profit .card-label { color: var(--green); }
    .hero-card-profit .card-sub   { color: rgba(76,175,80,0.6); }

    .hero-card-roi {
        background: linear-gradient(145deg, rgba(0,212,255,0.1) 0%, rgba(0,153,184,0.04) 100%);
        border-color: rgba(0,212,255,0.25);
        color:       var(--accent);
    }
    .hero-card-roi .card-label { color: var(--accent); }
    .hero-card-roi .card-sub   { color: rgba(0,212,255,0.55); }

    /* ── SECTION TITLES ── */
    .section-title {
        font-family:    'Rajdhani', sans-serif;
        font-size:      1.05rem;
        font-weight:    600;
        color:          var(--text-primary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        display:        flex;
        align-items:    center;
        gap:            0.55rem;
        margin-bottom:  0.55rem;
        padding-bottom: 0.35rem;
        border-bottom:  1px solid var(--border);
    }
    .section-title .title-icon { font-size: 1rem; }

    /* ── PATTERN CARDS ── */
    .pattern-card {
        background:    var(--bg-card);
        border:        1px solid var(--border);
        border-radius: 10px;
        padding:       0.85rem;
        margin-bottom: 0.6rem;
        position:      relative;
        transition:    border-color 0.2s, box-shadow 0.2s;
    }
    .pattern-card:hover {
        border-color: var(--border-hi);
        box-shadow:   0 2px 12px rgba(0,0,0,0.25);
    }
    .pattern-card.card-reroute  { border-left: 3px solid var(--green);  }
    .pattern-card.card-ignore   { border-left: 3px solid #546e7a;       }
    .pattern-card.card-alert    { border-left: 3px solid var(--amber);  }

    .pattern-card .card-header {
        display:        flex;
        align-items:    center;
        justify-content: space-between;
        margin-bottom:  0.45rem;
        flex-wrap:      wrap;
        gap:            0.35rem;
    }
    .pattern-card .card-header .pattern-name {
        font-family: 'Rajdhani', sans-serif;
        font-size:   0.88rem;
        font-weight: 600;
        color:       var(--text-primary);
    }

    /* Decision badges */
    .badge {
        display:        inline-flex;
        align-items:    center;
        gap:            0.28rem;
        padding:        2px 9px;
        border-radius:  20px;
        font-family:    'Rajdhani', sans-serif;
        font-size:      0.7rem;
        font-weight:    700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .badge-reroute { background: rgba(76,175,80,0.15); color: var(--green);  border: 1px solid rgba(76,175,80,0.3); }
    .badge-ignore  { background: rgba(84,110,122,0.15); color: #78909c;     border: 1px solid rgba(84,110,122,0.3); }
    .badge-alert   { background: rgba(255,183,77,0.13); color: var(--amber); border: 1px solid rgba(255,183,77,0.3); }

    .pattern-card .card-meta {
        display: flex;
        gap:     1rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }
    .pattern-card .meta-item {
        font-size: 0.72rem;
        color:     var(--text-dim);
    }
    .pattern-card .meta-item strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    .pattern-card .financials {
        display:        flex;
        gap:            0.6rem;
        flex-wrap:      wrap;
        margin-bottom:  0.5rem;
        padding:        0.4rem 0.55rem;
        background:     rgba(0,0,0,0.2);
        border-radius:  6px;
    }
    .pattern-card .fin-item {
        font-size: 0.7rem;
        color:     var(--text-dim);
    }
    .pattern-card .fin-item .fin-val {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size:   0.82rem;
    }
    .fin-val.pos { color: var(--green); }
    .fin-val.neg { color: var(--red);   }
    .fin-val.neu { color: var(--accent); }

    .confidence-bar-track {
        height:        4px;
        background:    rgba(255,255,255,0.08);
        border-radius: 2px;
        overflow:      hidden;
        margin-top:    0.45rem;
    }
    .confidence-bar-fill {
        height:     100%;
        border-radius: 2px;
        background: linear-gradient(90deg, var(--accent-dim), var(--accent));
        transition: width 0.6s ease;
    }
    .confidence-label {
        display:        flex;
        justify-content:space-between;
        font-size:      0.62rem;
        color:          var(--text-label);
        margin-top:     0.2rem;
        font-family:    'Inter', sans-serif;
    }

    /* ── EXECUTION FEED (TERMINAL) ── */
    .exec-feed {
        background:    var(--terminal-bg);
        border:        1px solid var(--border);
        border-radius: 10px;
        overflow:      hidden;
    }
    .exec-feed-header {
        background:    #0d1b2a;
        padding:       0.4rem 0.65rem;
        display:       flex;
        align-items:   center;
        gap:           0.35rem;
        border-bottom: 1px solid var(--border);
    }
    .exec-feed-header .dot {
        width: 9px; height: 9px;
        border-radius: 50%;
    }
    .exec-feed-header .dot-r { background: #ff5f57; }
    .exec-feed-header .dot-y { background: #febc2e; }
    .exec-feed-header .dot-g { background: #28c840; }
    .exec-feed-header .feed-title {
        font-family: 'Share Tech Mono', monospace;
        font-size:   0.68rem;
        color:       var(--text-label);
        margin-left: 0.55rem;
    }
    .exec-feed-body {
        padding:     0.7rem 0.75rem;
        max-height:  340px;
        overflow-y:  auto;
        font-family: 'Share Tech Mono', monospace;
        font-size:   0.72rem;
        line-height: 1.7;
        color:       var(--terminal-fg);
    }
    .exec-feed-body .log-line { margin: 0; white-space: pre-wrap; }
    .log-time    { color: #3a7ca5; }
    .log-success { color: var(--terminal-fg); }
    .log-reroute { color: var(--accent); }
    .log-alert   { color: var(--amber); }
    .log-ignore  { color: #546e7a; }
    .log-money   { color: #ffd54f; font-weight: 700; }
    .log-warn    { color: var(--amber); }
    .log-sub     { color: #2a5a7a; padding-left: 1.2rem; }

    /* Scrollbar for terminal */
    .exec-feed-body::-webkit-scrollbar       { width: 5px; }
    .exec-feed-body::-webkit-scrollbar-track  { background: transparent; }
    .exec-feed-body::-webkit-scrollbar-thumb  { background: var(--border); border-radius: 3px; }

    /* ── METRICS PANEL CARDS ── */
    .metrics-card {
        background:    var(--bg-card);
        border:        1px solid var(--border);
        border-radius: 10px;
        padding:       0.75rem 0.85rem;
        margin-bottom: 0.55rem;
    }
    .metrics-card-title {
        font-family:    'Rajdhani', sans-serif;
        font-size:      0.72rem;
        font-weight:    600;
        color:          var(--text-label);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom:  0.4rem;
    }

    /* ── SYSTEM STATUS WIDGET ── */
    .sys-status-row {
        display:        flex;
        align-items:    center;
        justify-content: space-between;
        padding:        0.28rem 0;
        border-bottom:  1px solid rgba(30,73,118,0.35);
        font-size:      0.72rem;
    }
    .sys-status-row:last-child { border-bottom: none; }
    .sys-status-row .sys-label { color: var(--text-dim); }
    .sys-status-row .sys-val   { color: var(--text-primary); font-weight: 500; font-family: 'Rajdhani', sans-serif; }
    .sys-status-row .sys-ok    { color: var(--green); }
    .sys-status-row .sys-warn  { color: var(--amber); }

    /* ── MISC UTILITIES ── */
    .dim-text { color: var(--text-dim) !important; font-size: 0.68rem !important; }
    .accent-text { color: var(--accent) !important; }
    .green-text  { color: var(--green) !important; }
    .red-text    { color: var(--red) !important; }
    .amber-text  { color: var(--amber) !important; }

    /* Plotly dark override */
    .plotly-graph-div {
        background: transparent !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
