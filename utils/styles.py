COMMON_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root {
    --app-bg:#f5f8fc; --surface:#fff; --ink:#172b4d; --muted:#64748b;
    --brand:#0b63ce; --brand-deep:#0a4fa3; --brand-soft:#eaf3ff;
    --line:#e2e8f0; --danger:#d92d20; --success:#12805c;
}
* { box-sizing:border-box; }
body, .stApp, .stMarkdown, input, textarea, button, select { font-family:'DM Sans',sans-serif; }
h1,h2,h3,h4 { font-family:'Plus Jakarta Sans',sans-serif !important; letter-spacing:0 !important; color:var(--ink); }
[data-testid="stAppViewContainer"] { background:var(--app-bg); }
[data-testid="stMainBlockContainer"] { max-width:1420px; padding-top:2rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b3f86 0%,#0b63ce 100%) !important; border-right:1px solid #0a4fa3; }
[data-testid="stSidebar"] * { color:#fff !important; }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.18); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#e8f1ff !important; }
footer,#MainMenu { visibility:hidden; }

/* Consistent Streamlit controls */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stDateInput input, .stTimeInput input, [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    border:1px solid var(--line) !important; border-radius:10px !important;
    background:var(--surface) !important; color:var(--ink) !important;
    min-height:44px; box-shadow:0 1px 2px rgba(15,23,42,.03);
}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus { border-color:var(--brand) !important; box-shadow:0 0 0 3px rgba(11,99,206,.12) !important; }
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    border-radius:10px !important; border:1px solid var(--line) !important;
    min-height:42px; font-weight:700 !important; transition:all .18s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover { border-color:var(--brand) !important; color:var(--brand) !important; transform:translateY(-1px); }
.stButton > button[kind="primary"] { background:var(--brand) !important; color:#fff !important; border-color:var(--brand) !important; }
.stButton > button[kind="primary"]:hover { background:var(--brand-deep) !important; color:#fff !important; }
[data-testid="stMetric"] { background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:16px; box-shadow:0 4px 16px rgba(15,23,42,.04); }
[data-testid="stMetricLabel"] { color:var(--muted) !important; font-weight:600; }
[data-testid="stMetricValue"] { color:var(--ink) !important; font-family:'Plus Jakarta Sans',sans-serif; }
[data-testid="stTabs"] button { font-weight:700; color:var(--muted); }
[data-testid="stTabs"] button[aria-selected="true"] { color:var(--brand) !important; }
[data-testid="stExpander"] { border:1px solid var(--line); border-radius:12px; background:var(--surface); overflow:hidden; }
[data-testid="stExpander"] summary:hover { background:var(--brand-soft); }
.stAlert { border-radius:12px !important; }

.page-kicker { color:var(--brand); font-size:12px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:5px; }
.section-title { display:flex; align-items:center; justify-content:space-between; margin:28px 0 14px; }
.section-title h2 { margin:0; font-size:20px; }
.section-title p { margin:4px 0 0; color:var(--muted); font-size:13px; }
.results-summary { color:var(--muted); font-size:13px; margin:14px 0 12px; }
.results-summary strong { color:var(--ink); font-size:15px; }

.app-header {
    background:linear-gradient(135deg,#0b3f86 0%,#0b63ce 100%);
    color:#fff; padding:26px 30px 24px; border-radius:18px;
    margin-bottom:20px; display:flex; align-items:center; gap:18px;
    box-shadow:0 10px 28px rgba(11,63,134,.18); position:relative; overflow:hidden;
}
.app-header:after { content:''; position:absolute; width:180px; height:180px; border:24px solid rgba(255,255,255,.08); border-radius:50%; right:-45px; top:-70px; }
.app-header h1 { margin:0; font-size:25px; font-weight:800; color:#fff !important; }
.app-header p  { margin:6px 0 0; opacity:.86; font-size:14px; color:#eaf3ff; }

.sos-banner {
    background:#fff4f2; color:#a3261a; border:1px solid #ffd5d0;
    padding:12px 18px; border-radius:12px; font-size:14px; font-weight:700;
    margin-bottom:20px; box-shadow:0 3px 12px rgba(217,45,32,.07);
}
@keyframes pulseRed {
    0%,100% { box-shadow:0 4px 18px rgba(229,57,53,.4); }
    50%      { box-shadow:0 4px 28px rgba(229,57,53,.75); }
}

.h-card {
    background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:18px 20px;
    margin-bottom:14px; box-shadow:0 3px 14px rgba(15,23,42,.045);
    border-left:4px solid var(--brand); transition:box-shadow .2s,transform .2s;
}
.h-card:hover { box-shadow:0 10px 24px rgba(15,23,42,.10); transform:translateY(-2px); }
.h-card.hosp  { border-left-color:#e53935; }
.h-card.clin  { border-left-color:#fb8c00; }
.h-card.pharm { border-left-color:#2e7d32; }
.h-card.blood { border-left-color:#c62828; }
.h-name   { font-size:16px; font-weight:800; color:var(--ink); margin:0 0 6px; }
.h-detail { font-size:13px; color:var(--muted); margin:3px 0; line-height:1.55; }

.badge { display:inline-block; padding:3px 11px; border-radius:20px;
         font-size:12px; font-weight:600; margin:2px 3px 2px 0; }
.b-blue   { background:#e8eaf6; color:#283593; }
.b-red    { background:#ffebee; color:#c62828; }
.b-green  { background:#e8f5e9; color:#2e7d32; }
.b-orange { background:#fff3e0; color:#e65100; }
.b-dist   { background:#e3f2fd; color:#1565c0; font-size:13px; padding:4px 13px; }
.b-purple { background:#f3e5f5; color:#6a1b9a; }

.action-btn { display:inline-block; padding:8px 15px; border-radius:8px;
              font-size:13px; font-weight:600; text-decoration:none; margin:3px 3px 0 0; }
.btn-dir  { background:#1565c0; color:#fff !important; }
.btn-call { background:#2e7d32; color:#fff !important; }
.btn-web  { background:#6a1b9a; color:#fff !important; }
.btn-save { background:#e65100; color:#fff !important; }

.welcome-card {
    background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:24px 18px;
    text-align:center; box-shadow:0 3px 14px rgba(15,23,42,.045);
    border-top:4px solid var(--brand); height:100%;
    transition:transform .2s;
}
.welcome-card:hover { transform:translateY(-3px); }
.welcome-card .icon { font-size:44px; margin-bottom:10px; }
.welcome-card h4    { margin:0 0 8px; color:var(--ink); }
.welcome-card p     { color:var(--muted); font-size:13px; line-height:1.5; }

.nav-card {
    background:var(--surface); border:1px solid var(--line); border-radius:14px; padding:20px;
    text-align:center; box-shadow:0 2px 10px rgba(0,0,0,.07);
    cursor:pointer; border:2px solid transparent;
    transition:all .2s; height:100%;
}

[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:14px !important; background:var(--surface); box-shadow:0 3px 14px rgba(15,23,42,.045); }
.nav-card:hover { border-color:#3949ab; transform:translateY(-3px); }

.emer-num-card {
    background:#fff; border-radius:12px; padding:14px;
    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,.07);
    border-top:3px solid #e53935;
}
.emer-num-card .num { font-size:22px; font-weight:800; color:#b71c1c; }
.emer-num-card .lbl { font-size:12px; color:#666; margin-top:3px; }

.sb-section {
    font-size:11px; font-weight:700; letter-spacing:1.2px;
    text-transform:uppercase; color:#90caf9 !important; margin:16px 0 8px;
}
.enum-item {
    display:flex; justify-content:space-between; align-items:center;
    background:rgba(255,255,255,.10); border-radius:8px;
    padding:8px 12px; margin-bottom:6px;
}
.enum-item .lbl { font-size:13px; }
.enum-item .num { font-size:16px; font-weight:800; color:#ffcc80; }

.stat-box {
    background:#fff; border-radius:12px; padding:16px;
    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,.07);
    border-bottom:3px solid #3949ab;
}
.stat-box .val { font-size:30px; font-weight:800; color:#1a237e; }
.stat-box .lbl { font-size:12px; color:#888; margin-top:2px; }

.sos-active {
    background:linear-gradient(135deg,#b71c1c,#e53935);
    color:#fff; border-radius:16px; padding:24px;
    text-align:center; animation:pulseRed 1s infinite;
    box-shadow:0 8px 30px rgba(229,57,53,.5);
}
.first-aid-card {
    background:#fff; border-radius:14px; padding:20px;
    margin-bottom:16px; box-shadow:0 2px 10px rgba(0,0,0,.07);
    border-left:5px solid #e53935;
}
.step-num {
    width:30px; height:30px; background:#1a237e; color:#fff;
    border-radius:50%; display:inline-flex; align-items:center;
    justify-content:center; font-weight:700; font-size:14px; margin-right:10px;
}
.blood-card {
    background:#fff; border-radius:12px; padding:14px;
    text-align:center; box-shadow:0 2px 8px rgba(0,0,0,.07);
    border-top:3px solid #c62828; margin-bottom:10px;
}
.blood-type { font-size:28px; font-weight:800; color:#b71c1c; }
</style>
"""
