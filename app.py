"""
app.py — SkillBridge: AI Career Guidance + Skill-Gap Analyzer
============================================================
Final-year B.E. project by Darshan Dalvi.

Pure logic lives in analyzer.py / roles_data.py / courses_data.py /
market_data.py / report.py / auth.py. This file is the Streamlit UI that
wires everything together:

  Input (resume / manual)  ->  gap analysis + charts + demand + salary + peer
                           ->  AI roadmap + suggested projects + courses
                           ->  progress tracker, compare-roles, resume check,
                               JD match, PDF export, login, theme toggle.
"""

import datetime
import streamlit as st
import plotly.graph_objects as go
from google import genai
import os
import streamlit.components.v1 as components

from roles_data import (
    ROLE_REQUIREMENTS, MASTER_SKILLS, ROLE_SALARY_IN,
    ROLE_BENCHMARK, DEFAULT_BENCHMARK,
)
from analyzer import (
    extract_text_from_pdf, extract_skills, analyze_gap,
    estimate_timeline, rank_in_demand, score_resume_quality, jd_match,
    ats_score, skill_categories,
)
from courses_data import get_courses
from market_data import curated_market, ai_market_pulse
from jobs_api import fetch_live_skills, match_live
from share_card import build_share_card
from report import build_report_pdf
import auth
import api_client

# ---------------------------------------------------------------- IN-BROWSER PDF READER
# A tiny static component that reads the chosen PDF *on the user's device* with pdf.js and
# returns the extracted text over the component channel (websocket) — bypassing Streamlit's
# file-upload endpoint, which fails on mobile (AxiosError: Network Error). No file is uploaded.
_PDF_READER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_reader")
try:
    _pdf_reader = components.declare_component("skillbridge_pdf_reader", path=_PDF_READER_DIR)
except Exception:
    _pdf_reader = None

# ---------------------------------------------------------------- PAGE CONFIG
st.set_page_config(page_title="SkillBridge — AI Career Analyzer",
                   page_icon="🎯", layout="wide")

# ---------------------------------------------------------------- STATE
ss = st.session_state
ss.setdefault("auth_user", None)
ss.setdefault("learned", [])
ss.setdefault("roadmap_text", "")
ss.setdefault("projects_text", "")
ss.setdefault("market_text", "")
ss.setdefault("chat", [])
ss.setdefault("interview_text", "")
ss.setdefault("session", None)
ss.theme = "light" if ss.get("theme_toggle", False) else "dark"

# ---------------------------------------------------------------- THEME / CSS
_VARS_DARK = """
:root{
 --bg-grad: radial-gradient(60vw 55vw at 12% -8%, rgba(34,197,94,0.20) 0%, transparent 60%),
            radial-gradient(55vw 50vw at 92% 6%, rgba(34,211,238,0.16) 0%, transparent 58%),
            linear-gradient(180deg,#070b16 0%,#04060d 100%);
 --text:#f8fafc; --sub:#94a3b8;
 --glass-bg:rgba(148,163,184,0.06); --glass-border:rgba(148,163,184,0.16);
 --have-bg:rgba(34,197,94,0.14); --have-fg:#86efac; --have-bd:rgba(34,197,94,0.42);
 --miss-bg:rgba(251,113,133,0.12); --miss-fg:#fda4af; --miss-bd:rgba(251,113,133,0.40);
 --bonus-bg:rgba(167,139,250,0.14); --bonus-fg:#c4b5fd; --bonus-bd:rgba(167,139,250,0.40);
 --accent1:#22c55e; --accent2:#22d3ee;
 --sidebar-bg:linear-gradient(180deg,#0b1322 0%,#070b16 100%);
 --field-bg:rgba(2,6,15,0.55); --field-fg:#f8fafc; --field-bd:rgba(148,163,184,0.20); --icon-invert:invert(0);
}
"""
_VARS_LIGHT = """
:root{
 --bg-grad: radial-gradient(60vw 55vw at 12% -8%, rgba(34,197,94,0.10) 0%, transparent 60%),
            radial-gradient(55vw 50vw at 92% 6%, rgba(34,211,238,0.10) 0%, transparent 58%),
            linear-gradient(180deg,#f6f9fc 0%,#eef2f8 100%);
 --text:#0f172a; --sub:#475569;
 --glass-bg:rgba(255,255,255,0.80); --glass-border:rgba(15,23,42,0.10);
 --have-bg:rgba(22,163,74,0.14); --have-fg:#15803d; --have-bd:rgba(22,163,74,0.40);
 --miss-bg:rgba(225,29,72,0.10); --miss-fg:#be123c; --miss-bd:rgba(225,29,72,0.32);
 --bonus-bg:rgba(124,58,237,0.10); --bonus-fg:#6d28d9; --bonus-bd:rgba(124,58,237,0.30);
 --accent1:#16a34a; --accent2:#0891b2;
 --sidebar-bg:linear-gradient(180deg,#eef2f8 0%,#e3e9f3 100%);
 --field-bg:#ffffff; --field-fg:#0f172a; --field-bd:#cbd5e1; --icon-invert:invert(1);
}
"""
_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, .stApp, [class*="css"]{ font-family:'DM Sans',system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }
.stApp{ background:var(--bg-grad); background-attachment:fixed; }
.stApp::before{ content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
  background-image:linear-gradient(rgba(148,163,184,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,184,.05) 1px,transparent 1px);
  background-size:46px 46px;
  -webkit-mask-image:radial-gradient(ellipse 75% 55% at 50% 0%,#000 35%,transparent 80%);
  mask-image:radial-gradient(ellipse 75% 55% at 50% 0%,#000 35%,transparent 80%);}
[data-testid="stAppViewContainer"] .block-container{ position:relative; z-index:1; }
h1,h2,h3,h4,h5,h6{ font-family:'Space Grotesk','DM Sans',sans-serif; letter-spacing:-0.01em; }
.hero-title{ font-family:'Space Grotesk',sans-serif; font-size:3.1rem; font-weight:700;
  text-align:center; background:linear-gradient(110deg,#22c55e,#22d3ee 55%,#a78bfa);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  margin-bottom:0; letter-spacing:-0.02em;}
.hero-sub{ text-align:center; color:var(--sub); font-family:'DM Sans'; font-size:0.86rem;
  letter-spacing:3px; text-transform:uppercase; margin:8px 0 16px; font-weight:500;}
.glass{ background:var(--glass-bg); border:1px solid var(--glass-border); border-radius:18px;
  padding:20px; backdrop-filter:blur(14px); margin-bottom:14px; color:var(--text);}
.score-ring{ font-family:'Space Grotesk'; font-size:3.4rem; font-weight:700;
  background:linear-gradient(120deg,var(--accent1),var(--accent2));
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;}
.pill{ display:inline-block; padding:6px 14px; margin:3px; border-radius:999px;
  font-size:0.82rem; font-family:'DM Sans'; font-weight:500;}
.pill-have{ background:var(--have-bg); color:var(--have-fg); border:1px solid var(--have-bd);}
.pill-miss{ background:var(--miss-bg); color:var(--miss-fg); border:1px solid var(--miss-bd);}
.pill-bonus{ background:var(--bonus-bg); color:var(--bonus-fg); border:1px solid var(--bonus-bd);}
.pill-hot{ background:rgba(245,158,11,0.14); color:#fbbf24; border:1px solid rgba(245,158,11,0.45);}
.salary{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.95rem;
  color:var(--have-fg); letter-spacing:-0.01em; line-height:1.12; margin:2px 0; }
/* light-mode legibility: native captions + markdown headings follow the theme */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{ color:var(--sub) !important; }
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4{ color:var(--text) !important; }
.sec-label{ font-family:'Space Grotesk'; font-weight:600; color:var(--text); font-size:1.0rem;
  margin:14px 0 8px; letter-spacing:-0.01em;}
.stButton>button{ background:linear-gradient(135deg,#22c55e,#16a34a);
  color:#04130a; border:0; border-radius:12px; font-family:'DM Sans'; font-weight:700;
  padding:9px 20px; transition:transform .15s,box-shadow .2s;
  box-shadow:0 10px 26px -12px rgba(34,197,94,.8);}
.stButton>button:hover{ transform:translateY(-1px); box-shadow:0 14px 32px -12px rgba(34,197,94,.95);}
.stButton>button:active{ transform:translateY(1px);}
[data-testid="stSidebar"]{ background:var(--sidebar-bg) !important; border-right:1px solid var(--glass-border);}
.stProgress > div > div > div{ background:linear-gradient(90deg,#22c55e,#22d3ee) !important; }
.stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"] p { color:var(--sub); font-weight:600; }
.stTabs [data-baseweb="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] p { color:var(--text); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ background:linear-gradient(90deg,#22c55e,#22d3ee) !important; }
/* native text widgets follow the theme text colour */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color:var(--text) !important; }
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] label p { color:var(--text) !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color:var(--text); }
[role="radiogroup"] label, [role="radiogroup"] label p { color:var(--text) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] span, [data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:var(--text) !important; }
/* top header bar -> transparent so it follows the page background in both themes */
[data-testid="stHeader"], header[data-testid="stHeader"]{ background:transparent !important; }
/* file uploader: dropzone AND the uploaded-file chip -> fully theme-aware */
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] > div > section,
section[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderDropzone"]{ background:var(--field-bg) !important;
  border:1px dashed var(--field-bd) !important; }
[data-testid="stFileUploaderFile"]{ background:var(--field-bg) !important;
  border:1px solid var(--field-bd) !important; border-radius:8px; }
[data-testid="stFileUploaderFile"] div{ background:transparent !important; }
[data-testid="stFileUploader"] *{ color:var(--field-fg) !important; }
[data-testid="stFileUploader"] svg{ fill:var(--field-fg) !important; }
[data-testid="stFileUploader"] button{ background:var(--field-bg) !important;
  color:var(--field-fg) !important; border:1px solid var(--field-bd) !important; }
/* uploaded-file CHIP (Streamlit's newer testid, rendered outside stFileUploader) */
[data-testid="stFileChips"]{ background:transparent !important; }
[data-testid="stFileChip"]{ background:var(--field-bg) !important;
  border:1px solid var(--field-bd) !important; border-radius:8px;
  color:var(--field-fg) !important; }
[data-testid="stFileChip"] *{ color:var(--field-fg) !important; background:transparent !important; }
[data-testid="stFileChip"] svg{ fill:var(--field-fg) !important; color:var(--field-fg) !important; }
[data-testid="stFileChipDeleteButton"] svg, [data-testid="stFileChip"] button svg{
  fill:var(--field-fg) !important; }
.stTextInput input, .stTextArea textarea, [data-baseweb="input"],
[data-baseweb="base-input"], [data-baseweb="textarea"]{
  background:var(--field-bg) !important; color:var(--field-fg) !important;
  border-color:var(--field-bd) !important; }
/* input/textarea/chat placeholders -> muted theme colour so they're readable in light mode
   (default placeholder grey was invisible on the white field). */
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-baseweb="input"] input::placeholder, [data-baseweb="base-input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder, [data-testid="stChatInputTextArea"]::placeholder{
  color:var(--sub) !important; -webkit-text-fill-color:var(--sub) !important; opacity:0.9 !important; }
[data-baseweb="select"] > div{ background:var(--field-bg) !important;
  border-color:var(--field-bd) !important; }
[data-baseweb="select"] div, [data-baseweb="select"] span,
[data-baseweb="select"] svg{ color:var(--field-fg) !important; fill:var(--field-fg) !important; }
[data-testid="stChatInput"] textarea{ background:var(--field-bg) !important;
  color:var(--field-fg) !important; }
.stButton>button{ color:#04130a !important; }
/* protect coloured elements from the broad text rules above */
.pill-have{ color:var(--have-fg) !important; }
.pill-miss{ color:var(--miss-fg) !important; }
.pill-bonus{ color:var(--bonus-fg) !important; }
.pill-hot{ color:#ff9d2e !important; }
/* containers that use Streamlit's dark secondary bg -> make them theme-aware */
[data-testid="stChatInput"]{ background:var(--field-bg) !important; }
[data-testid="stChatInput"] > div{ background:var(--field-bg) !important;
  border:1px solid var(--field-bd) !important; border-radius:12px; }
[data-testid="stChatInput"] textarea{ background:transparent !important;
  color:var(--field-fg) !important; }
[data-testid="stChatInput"] button{ background:transparent !important; }
[data-testid="stChatInput"] svg{ fill:var(--field-fg) !important; }
[data-testid="stExpander"]{ background:var(--glass-bg) !important;
  border:1px solid var(--glass-border) !important; border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary,
[data-testid="stExpander"] details > div{ background:transparent !important; }
[data-testid="stChatMessage"]{ background:var(--glass-bg) !important; border-radius:12px; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li{ color:var(--text) !important; }
[data-testid="stFileUploaderFile"], [data-testid="stFileUploaderFile"] *,
[data-testid="stFileUploaderDeleteBtn"] svg{ color:var(--field-fg) !important;
  fill:var(--field-fg) !important; }
/* radio selection circles: empty unselected circle follows the field bg;
   selected circle keeps the accent colour (only unselected is restyled) */
[data-baseweb="radio"]:not(:has(input:checked)) > div:first-child,
[data-baseweb="radio"]:not(:has(input:checked)) > div:first-child > div{
  background:var(--field-bg) !important; border-color:var(--field-bd) !important; }
/* Streamlit's header toolbar (Share / GitHub / edit / star / menu) + the sidebar collapse
   arrow live INSIDE the app. Their icons are Material-font glyphs (stIconMaterial, coloured
   via `color`) plus a few svgs, so set BOTH color and fill to the theme text colour -> they
   stay visible in light AND dark mode. */
[data-testid="stToolbar"], [data-testid="stToolbar"] *,
[data-testid="stToolbarActions"], [data-testid="stToolbarActions"] *,
[data-testid="stToolbarActionButton"], [data-testid="stToolbarActionButton"] *,
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebarHeader"] [data-testid="stIconMaterial"],
[data-testid="stHeader"] [data-testid="stIconMaterial"],
[data-testid="stMainMenu"], [data-testid="stMainMenu"] *{
  color:var(--text) !important; fill:var(--text) !important; opacity:1 !important; }
[data-testid="stHeader"] svg, [data-testid="stToolbar"] svg,
[data-testid="stToolbarActions"] svg{ fill:var(--text) !important; color:var(--text) !important; }
/* Toolbar action icons (star / edit / GitHub) are baked-white SVG background-images, so
   color/fill can't touch them -> invert them to dark in light mode (left white in dark). */
[data-testid="stToolbarActionButtonIcon"], [data-testid="stToolbarActionButton"] [data-testid="stToolbarActionButtonIcon"]{
  filter: var(--icon-invert) !important; }
"""


def inject_theme():
    vars_block = _VARS_LIGHT if ss.theme == "light" else _VARS_DARK
    st.markdown("<style>" + vars_block + _BASE_CSS + "</style>", unsafe_allow_html=True)


inject_theme()
CHART_FONT = "#16202e" if ss.theme == "light" else "#e6eef8"
# Hide Plotly's hover toolbar (zoom/pan/reset are no-ops on pie/radar and
# unreliable on touch); charts stay clean and still show hover tooltips.
_PLOTLY_CFG = {"displayModeBar": False}

# ---------------------------------------------------------------- API KEY
def get_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    import os
    return os.environ.get("GEMINI_API_KEY", "")


API_KEY = get_api_key()


def gemini_generate(prompt: str, model: str = "gemini-2.5-flash"):
    if not API_KEY:
        return None, "no_key"
    try:
        client = genai.Client(api_key=API_KEY)
        resp = client.models.generate_content(model=model, contents=prompt)
        return resp.text, None
    except Exception as e:
        return None, str(e)


def show_ai_error(err: str):
    if err == "no_key":
        st.info("**Add your free Gemini API key** to use AI features "
                "(`.streamlit/secrets.toml` → `GEMINI_API_KEY`).")
    elif "RESOURCE_EXHAUSTED" in err or "429" in err:
        st.warning("⏳ The free Gemini tier allows only a few requests per minute. "
                   "Please wait ~30 seconds and try again.")
    else:
        st.error(f"Something went wrong: {err}")


def pills(skills, cls):
    if not skills:
        return "_None_"
    return " ".join(f'<span class="pill {cls}">{s}</span>' for s in skills)


@st.cache_data(ttl=1800, show_spinner="Pulling live job-market data…")
def cached_live_skills(role):
    """Cache live job-market fetch per role (30 min) so Adzuna isn't hit on
    every rerun and the demo stays snappy."""
    return fetch_live_skills(role)


# ---------------------------------------------------------------- SIDEBAR
with st.sidebar:
    top_box = st.container()  # account + theme show here (visually first)

    # Skills & role are instantiated FIRST so the login/logout reruns in the
    # account box below can never discard the user's selected skills.
    st.markdown("### 🎯 Your Target")
    target_role = st.selectbox("Target role you want:", list(ROLE_REQUIREMENTS.keys()))
    method = st.radio("How to provide your skills:",
                      ["📄 Upload Resume (PDF)", "📋 Paste Resume Text",
                       "✅ Select Skills Manually"])

    resume_text = ""
    base_skills = []
    if method == "📄 Upload Resume (PDF)":
        pdf_text = ""
        if _pdf_reader is not None:
            st.caption("Pick your PDF below — it is read **on your device** "
                       "(nothing is uploaded), so it works on phones too.")
            pdf_text = _pdf_reader(key="pdf_reader_main", default="") or ""
            if not (pdf_text and pdf_text.strip()):
                with st.expander("Trouble picking a file? Use the classic uploader"):
                    _up = st.file_uploader("Upload your resume", type=["pdf"], key="main_resume")
                    if _up:
                        _t = extract_text_from_pdf(_up)
                        pdf_text = "" if _t.startswith("__ERROR__") else _t
        else:
            _up = st.file_uploader("Upload your resume", type=["pdf"], key="main_resume")
            if _up:
                _t = extract_text_from_pdf(_up)
                pdf_text = "" if _t.startswith("__ERROR__") else _t
        if pdf_text and pdf_text.strip():
            resume_text = pdf_text
            base_skills = extract_skills(resume_text)
            st.success(f"Found {len(base_skills)} skills in your resume.")
    elif method == "📋 Paste Resume Text":
        resume_text = st.text_area(
            "Paste your resume text here:", height=200, key="resume_paste",
            placeholder="Open your resume, select all (Ctrl+A), copy, and paste it here…")
        if resume_text.strip():
            base_skills = extract_skills(resume_text)
            st.success(f"Found {len(base_skills)} skills in your pasted resume.")
        else:
            st.caption("Works great on mobile — no file upload needed.")
    else:
        base_skills = st.multiselect("Select all skills you currently know:",
                                     MASTER_SKILLS, key="manual_skills")

    ss.student_skills = base_skills
    ss.resume_text = resume_text
    st.caption("Built by Darshan Dalvi · Final-year B.E. Project\n\n"
               "Python · NLP · Gemini · Streamlit · Plotly")

    with top_box:
        st.markdown("### 👤 Account")
        if ss.auth_user:
            st.success(f"Logged in as **{ss.auth_user}**")
            _store = "☁️ Backend" if api_client.is_api(ss.session) else "💾 Local (backend offline)"
            st.caption(f"Saving to: {_store}")
            if st.button("Log out"):
                ss.auth_user = None
                ss.session = None
                ss.learned = []
                ss.chat = []
                ss.pop("_last_saved_sig", None)
                st.rerun()
        else:
            mode = st.radio("Account", ["Log in", "Register"], horizontal=True,
                            label_visibility="collapsed")
            u = st.text_input("Username", key="auth_u")
            p = st.text_input("Password", type="password", key="auth_p")
            if st.button(mode):
                ok, msg, sess = (api_client.register(u, p) if mode == "Register"
                                 else api_client.authenticate(u, p))
                if ok:
                    ss.auth_user = sess["username"]
                    ss.session = sess
                    ss.learned = api_client.get_progress(sess, ss.auth_user).get("learned", [])
                    st.rerun()
                else:
                    st.error(msg)
            st.caption("Login saves your data to the SkillBridge backend "
                       "(falls back to local storage if it isn't running).")
        st.markdown("---")
        _theme_label = "☀️ Light mode" if ss.theme == "light" else "🌙 Dark mode"
        st.toggle(_theme_label, key="theme_toggle")
        st.markdown("---")

# ---------------------------------------------------------------- HEADER
st.markdown('<p class="hero-title">SkillBridge</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI CAREER GUIDANCE · SKILL-GAP ANALYZER</p>',
            unsafe_allow_html=True)

student_skills = ss.student_skills
result = analyze_gap(student_skills, target_role) if student_skills else None

# Auto-persist profile + each new analysis to the backend (when logged in & online).
# A signature guard saves once per unique (role, skills) combo, not on every rerun.
if ss.auth_user and student_skills and result:
    _sig = (target_role, tuple(sorted(student_skills)))
    if ss.get("_last_saved_sig") != _sig:
        api_client.save_profile(ss.session, target_role, student_skills,
                                ss.get("resume_text", ""))
        api_client.save_analysis(ss.session, target_role, result["match_percent"],
                                 result["readiness"],
                                 result["matched_core"] + result["matched_bonus"],
                                 result["all_missing"])
        ss._last_saved_sig = _sig

tabs = st.tabs(["📊 Analyze", "🔴 Live Match", "🤖 Roadmap & Courses",
                "✅ Progress Tracker", "⚖️ Compare Roles", "📄 Resume Check",
                "🎯 JD Match", "💬 AI Mentor"])

# ============================================================ TAB 1: ANALYZE
with tabs[0]:
    if not result:
        st.info("👈 Add your skills in the sidebar (upload a resume or select manually) "
                "to see your personalized analysis.")
    else:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.markdown(f'<div class="score-ring">{result["match_percent"]}%</div>',
                        unsafe_allow_html=True)
            st.caption(f"Role match · {result['readiness']}")
        with c2:
            have_n = len(result["matched_core"]) + len(result["matched_bonus"])
            miss_n = len(result["all_missing"])
            fig = go.Figure(go.Pie(
                labels=["Skills you have", "Skills to learn"],
                values=[have_n, miss_n], hole=0.55,
                marker_colors=["#00d39a", "#ff6b85"]))
            fig.update_layout(height=210, margin=dict(t=10, b=10, l=10, r=10),
                              paper_bgcolor="rgba(0,0,0,0)", font_color=CHART_FONT,
                              showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(fig, width="stretch", config=_PLOTLY_CFG)
        with c3:
            sal = ROLE_SALARY_IN.get(target_role)
            if sal:
                st.markdown('<div class="sec-label">💰 Fresher salary (India)</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="salary">₹{sal["low"]}–{sal["high"]} LPA</div>', unsafe_allow_html=True)
                st.caption(f"Median ≈ ₹{sal['median']} LPA · indicative, varies by "
                           "company/city/skills.")

        st.progress(result["match_percent"] / 100)

        st.markdown('<div class="sec-label">✅ Skills you already have</div>',
                    unsafe_allow_html=True)
        st.markdown(pills(result["matched_core"] + result["matched_bonus"], "pill-have"),
                    unsafe_allow_html=True)

        # Skills in demand (bar) + badges
        st.markdown('<div class="sec-label">🔥 Missing skills — ranked by employer '
                    'demand</div>', unsafe_allow_html=True)
        ranked = rank_in_demand(result["all_missing"])
        if ranked:
            top = ranked[:10]
            fig2 = go.Figure(go.Bar(
                x=[s for s, _, _ in top], y=[d for _, d, _ in top],
                marker_color=["#ff9d2e" if hi else "#7b8cff" for _, _, hi in top]))
            fig2.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color=CHART_FONT, yaxis_title="Demand score")
            st.plotly_chart(fig2, width="stretch", config=_PLOTLY_CFG)
            hot = [s for s, _, hi in ranked if hi]
            if hot:
                st.markdown("**Most in-demand of your gaps:** " +
                            " ".join(f'<span class="pill pill-hot">🔥 {s}</span>' for s in hot),
                            unsafe_allow_html=True)
        else:
            st.success("No missing skills — you cover this role! 🎉")

        # Peer comparison
        st.markdown('<div class="sec-label">🧭 Peer comparison</div>',
                    unsafe_allow_html=True)
        bench = ROLE_BENCHMARK.get(target_role, DEFAULT_BENCHMARK)
        figp = go.Figure(go.Bar(
            x=[result["match_percent"], bench], y=["You", "Typical applicant"],
            orientation="h", marker_color=["#00d39a", "#9aa7bd"]))
        figp.update_layout(height=160, margin=dict(t=6, b=6, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT, xaxis_title="Match %", xaxis_range=[0, 100])
        st.plotly_chart(figp, width="stretch", config=_PLOTLY_CFG)
        st.caption("⚠️ Indicative benchmark (our rubric), not real candidate data.")

        # Skill radar (coverage by category)
        st.markdown('<div class="sec-label">🕸️ Skill radar — coverage by area</div>',
                    unsafe_allow_html=True)
        cats = skill_categories(target_role, student_skills)
        if len(cats) >= 3:
            labels = [c for c, _, _ in cats]
            vals = [p for _, p, _ in cats]
            figr = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=labels + [labels[0]], fill="toself",
                line_color="#00d39a", fillcolor="rgba(0,211,154,0.25)"))
            figr.update_layout(height=330, margin=dict(t=30, b=20, l=50, r=50),
                               paper_bgcolor="rgba(0,0,0,0)", font_color=CHART_FONT,
                               polar=dict(bgcolor="rgba(0,0,0,0)",
                                          radialaxis=dict(range=[0, 100],
                                              tickfont=dict(color=CHART_FONT)),
                                          angularaxis=dict(tickfont=dict(color=CHART_FONT))))
            st.plotly_chart(figr, width="stretch", config=_PLOTLY_CFG)
        else:
            st.caption("Add a few more skills to unlock the category radar.")

        # Shareable result card (PNG for LinkedIn)
        st.markdown('<div class="sec-label">📣 Shareable result card</div>',
                    unsafe_allow_html=True)
        try:
            readiness_clean = result["readiness"].encode("ascii", "ignore").decode().strip()
            card_png = build_share_card(target_role, result["match_percent"],
                                        readiness_clean, name=ss.auth_user or "",
                                        top_skills=result["all_missing"][:6])
            st.image(card_png, caption="Post this on LinkedIn 🚀", width=440)
            st.download_button("⬇️ Download share card (PNG)", data=card_png,
                               file_name=f"SkillBridge_{target_role.replace(' ', '_')}_card.png",
                               mime="image/png")
        except Exception as e:
            st.caption(f"Card unavailable: {e}")

        # PDF download
        st.markdown('<div class="sec-label">📄 Take your results with you</div>',
                    unsafe_allow_html=True)
        timeline = estimate_timeline(result["all_missing"])
        try:
            pdf_bytes = build_report_pdf({
                "name": ss.auth_user or "Student", "role": target_role,
                "generated_on": datetime.date.today().isoformat(),
                "result": result, "timeline": timeline,
                "salary": ROLE_SALARY_IN.get(target_role),
                "resume_score": score_resume_quality(ss.get("resume_text", "")) if ss.get("resume_text") else None,
                "roadmap_text": ss.roadmap_text or None,
                "projects_text": ss.projects_text or None,
            })
            st.download_button("⬇️ Download PDF report", data=pdf_bytes,
                               file_name=f"SkillBridge_{target_role.replace(' ', '_')}.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF unavailable: {e}")

# ============================================================ TAB: LIVE MATCH
with tabs[1]:
    st.markdown('<div class="sec-label">🔴 Live job-market match — your skills vs what '
                'employers are actually asking for right now.</div>',
                unsafe_allow_html=True)
    if not student_skills:
        st.info("👈 Add your skills in the sidebar to match against the live market.")
    else:
        ranked, meta = cached_live_skills(target_role)
        if meta.get("source") == "adzuna":
            st.success(f"🔴 LIVE — analysed {meta.get('jobs', 0)} real job ads for "
                       f"{target_role} in India (Adzuna API).")
            suffix = " jobs"
        else:
            st.warning("Showing the curated demand index (always-on fallback). Add a free "
                       "Adzuna key (ADZUNA_APP_ID / ADZUNA_APP_KEY in secrets.toml) to match "
                       "against REAL job postings.")
            suffix = "/100"
        lm = match_live(student_skills, ranked)

        c1, c2, c3 = st.columns([1.3, 1, 1])
        with c1:
            st.markdown(f'<div class="score-ring">{lm["match_percent"]}%</div>',
                        unsafe_allow_html=True)
            st.caption("Live-demand match (weighted by how often each skill appears)")
        c2.metric("In-demand skills you have", len(lm["have"]))
        c3.metric("In-demand skills missing", len(lm["missing"]))

        top = ranked[:12]
        haveset = {sk for sk, _ in lm["have"]}
        figL = go.Figure(go.Bar(
            x=[sk for sk, _ in top], y=[c for _, c in top],
            marker_color=["#00d39a" if sk in haveset else "#ff6b85" for sk, _ in top],
            text=["✓" if sk in haveset else "✗" for sk, _ in top], textposition="outside"))
        figL.update_layout(height=330, margin=dict(t=26, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT,
                           yaxis_title=("mentions in real jobs" if suffix == " jobs" else "demand"))
        st.plotly_chart(figL, width="stretch", config=_PLOTLY_CFG)
        st.caption("🟢 you have it · 🔴 you're missing it · bar height = real demand")

        st.markdown('<div class="sec-label">🔥 Most-wanted skills you\'re missing '
                    '(ordered by real demand)</div>', unsafe_allow_html=True)
        if lm["missing"]:
            st.markdown(" ".join(f'<span class="pill pill-miss">{sk} · {c}{suffix}</span>'
                                 for sk, c in lm["missing"][:12]), unsafe_allow_html=True)
        else:
            st.success("You already cover every in-demand skill for this role! 🎉")

        st.markdown('<div class="sec-label">✅ In-demand skills you already have</div>',
                    unsafe_allow_html=True)
        st.markdown(" ".join(f'<span class="pill pill-have">{sk} · {c}{suffix}</span>'
                             for sk, c in lm["have"][:12]) or "_None yet_",
                    unsafe_allow_html=True)
        st.caption("This matches you against REAL employer demand, not just a fixed list — "
                   "so you learn what the market wants today.")


# ============================================================ TAB 2: ROADMAP
with tabs[2]:
    if not result:
        st.info("👈 Add your skills first to generate a roadmap.")
    else:
        missing = result["all_missing"]
        timeline = estimate_timeline(missing)
        m1, m2, m3 = st.columns(3)
        m1.metric("Skills to learn", len(missing))
        m2.metric("Est. study time", f"~{timeline['total_hours']} hrs")
        m3.metric("Time to job-ready", f"~{timeline['months']} months",
                  help="At ~10 hrs/week. Adjustable assumption.")

        if not missing:
            st.success("You already meet this role's requirements — build projects "
                       "and start applying! 🚀")
        else:
            # AI Roadmap
            st.markdown('<div class="sec-label">🤖 AI learning roadmap</div>',
                        unsafe_allow_html=True)
            st.selectbox("Roadmap language:", ["English", "Hindi", "Marathi"],
                         key="roadmap_lang")
            if st.button("✨ Generate / Regenerate Roadmap"):
                prompt = (
                    "You are an expert career mentor for Indian students.\n"
                    f"A final-year engineering student wants to become a {target_role}.\n"
                    f"They still need to learn: {', '.join(missing)}.\n\n"
                    "Create a clear, motivating, step-by-step roadmap that:\n"
                    "- Groups skills into a logical learning order (phases)\n"
                    "- For each skill: what to learn, ONE free resource, a realistic time\n"
                    "- Ends with 2 project ideas combining these skills\n"
                    "Use headings and short bullets. Be encouraging.\n"
                    f"Write the ENTIRE response in {ss.get('roadmap_lang', 'English')}.")
                with st.spinner("AI mentor is designing your roadmap…"):
                    text, err = gemini_generate(prompt)
                if err:
                    show_ai_error(err)
                else:
                    ss.roadmap_text = text
            if ss.roadmap_text:
                st.markdown(ss.roadmap_text)

            # Suggested projects
            st.markdown('<div class="sec-label">💡 Suggested portfolio projects</div>',
                        unsafe_allow_html=True)
            if st.button("🛠️ Suggest projects that cover several gaps"):
                prompt = (
                    f"Suggest 3 portfolio project ideas for a student targeting {target_role}. "
                    f"Each project should cover SEVERAL of these missing skills at once: "
                    f"{', '.join(missing)}. For each: a catchy title, 2-line description, "
                    "the skills it covers, and a difficulty (Beginner/Intermediate/Advanced). "
                    "Keep it concise with bullets.")
                with st.spinner("Designing project ideas…"):
                    text, err = gemini_generate(prompt)
                if err:
                    show_ai_error(err)
                else:
                    ss.projects_text = text
            if ss.projects_text:
                st.markdown(ss.projects_text)

            # Interview readiness
            st.markdown('<div class="sec-label">🎤 Interview readiness</div>',
                        unsafe_allow_html=True)
            if st.button("🧠 Likely interview questions for this role"):
                have_list = ", ".join(result["matched_core"] + result["matched_bonus"]) or "the basics"
                prompt = (
                    f"Act as an interviewer hiring a fresher {target_role} in India.\n"
                    f"The candidate currently knows: {have_list}.\n"
                    "List 8 likely interview questions (6 technical + 2 HR), grouped by topic, "
                    "then 3 quick preparation tips. Concise bullets.")
                with st.spinner("Preparing interview questions…"):
                    text, err = gemini_generate(prompt)
                if err:
                    show_ai_error(err)
                else:
                    ss.interview_text = text
            if ss.interview_text:
                st.markdown(ss.interview_text)

            # Curated course links
            st.markdown('<div class="sec-label">🎓 Free courses for your missing skills</div>',
                        unsafe_allow_html=True)
            for skill in missing[:12]:
                links = get_courses(skill)
                links_md = " · ".join(f"[{c['title']}]({c['url']})" for c in links)
                st.markdown(f"**{skill}** — {links_md}")

# ============================================================ TAB 3: PROGRESS
with tabs[3]:
    if not result:
        st.info("👈 Add your skills first to track progress.")
    else:
        st.markdown('<div class="sec-label">Tick skills as you learn them and watch '
                    'your match score climb.</div>', unsafe_allow_html=True)
        missing = result["all_missing"]
        if not missing:
            st.success("Nothing left to learn for this role — 100%! 🎉")
        else:
            cols = st.columns(2)
            new_learned = []
            for i, skill in enumerate(missing):
                with cols[i % 2]:
                    if st.checkbox(skill, value=(skill in ss.learned), key=f"lrn_{skill}"):
                        new_learned.append(skill)
            ss.learned = new_learned

            projected = analyze_gap(list(set(student_skills) | set(new_learned)), target_role)
            a, b = st.columns(2)
            a.metric("Current match", f"{result['match_percent']}%")
            b.metric("Projected match", f"{projected['match_percent']}%",
                     delta=f"{projected['match_percent'] - result['match_percent']}%")
            st.progress(projected["match_percent"] / 100)

            if ss.auth_user:
                if st.button("💾 Save my progress"):
                    ok = api_client.save_progress(ss.session, ss.auth_user, target_role,
                                                  projected["match_percent"], new_learned)
                    ss.learned = new_learned
                    if ok and api_client.is_api(ss.session):
                        st.success("Progress saved to your account (backend).")
                    elif ok:
                        st.success("Progress saved locally (backend offline).")
                    else:
                        st.warning("Couldn't save progress right now.")
                hist = api_client.get_history(ss.session)
                if hist and len(hist) >= 2:
                    st.markdown('<div class="sec-label">📈 Your match score over time</div>',
                                unsafe_allow_html=True)
                    figh = go.Figure(go.Scatter(
                        x=list(range(1, len(hist) + 1)),
                        y=[h.get("score", 0) for h in hist],
                        mode="lines+markers", line_color="#00d39a", marker=dict(size=8)))
                    figh.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10),
                                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                       font_color=CHART_FONT, yaxis_title="Match %",
                                       yaxis_range=[0, 100], xaxis_title="saved snapshots")
                    st.plotly_chart(figh, width="stretch", config=_PLOTLY_CFG)
                    st.caption(f"{len(hist)} saved snapshots — your readiness over time.")
                with st.expander("☁️ Your saved data (backend)"):
                    data = api_client.export_all(ss.session)
                    if data:
                        cprof = data.get("profile", {})
                        st.markdown(
                            f"- **Profile:** {cprof.get('target_role', '—')} · "
                            f"{len(cprof.get('skills', []))} skills\n"
                            f"- **Analyses saved:** {len(data.get('analyses', []))}\n"
                            f"- **Progress snapshots:** {len(data.get('progress', {}).get('history', []))}\n"
                            f"- **JD matches saved:** {len(data.get('jd_matches', []))}\n"
                            f"- **Mentor messages saved:** {len(data.get('chats', []))}")
                        import json as _json
                        st.download_button(
                            "⬇️ Download all my data (JSON)",
                            data=_json.dumps(data, indent=2, ensure_ascii=False),
                            file_name=f"skillbridge_{ss.auth_user}_data.json",
                            mime="application/json")
                    else:
                        st.caption("Backend offline — your data is being saved locally instead.")
            else:
                st.caption("🔑 Log in (sidebar) to save your progress across sessions.")

# ============================================================ TAB 4: COMPARE
with tabs[4]:
    if not student_skills:
        st.info("👈 Add your skills first to compare roles.")
    else:
        st.markdown('<div class="sec-label">See how ready you are for two roles at once '
                    '— choose realistically.</div>', unsafe_allow_html=True)
        roles = list(ROLE_REQUIREMENTS.keys())
        cc1, cc2 = st.columns(2)
        roleA = cc1.selectbox("Role A", roles, index=roles.index(target_role))
        roleB = cc2.selectbox("Role B", roles,
                              index=(roles.index(target_role) + 1) % len(roles))
        rA = analyze_gap(student_skills, roleA)
        rB = analyze_gap(student_skills, roleB)
        cc1.metric(roleA, f"{rA['match_percent']}%", rA["readiness"])
        cc2.metric(roleB, f"{rB['match_percent']}%", rB["readiness"])

        figc = go.Figure(go.Bar(
            x=[roleA, roleB], y=[rA["match_percent"], rB["match_percent"]],
            marker_color=["#00d39a", "#7b2ff7"], text=[f"{rA['match_percent']}%",
            f"{rB['match_percent']}%"], textposition="auto"))
        figc.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT, yaxis_title="Match %", yaxis_range=[0, 100])
        st.plotly_chart(figc, width="stretch", config=_PLOTLY_CFG)

        better = roleA if rA["match_percent"] >= rB["match_percent"] else roleB
        st.success(f"You're currently a stronger fit for **{better}**.")

# ============================================================ TAB 5: RESUME CHECK
with tabs[5]:
    st.markdown('<div class="sec-label">Resume quality check — beyond skills: structure, '
                'links and completeness.</div>', unsafe_allow_html=True)
    if ss.get("resume_text"):
        rq = score_resume_quality(ss.resume_text)
        st.markdown(f"### Resume score: {rq['score']}/100  ·  {rq['word_count']} words")
        st.progress(rq["score"] / 100)
        if rq["passed"]:
            st.markdown("**✅ Present:** " + ", ".join(rq["passed"]))
        if rq["issues"]:
            st.markdown("**⚠️ Improve:**")
            for lbl, tip in rq["issues"]:
                st.markdown(f"- **{lbl}** — {tip}")

        ats = ats_score(ss.resume_text, student_skills)
        st.markdown(f"### 🤖 ATS-friendliness: {ats['score']}/100")
        st.progress(ats["score"] / 100)
        st.caption("Most companies screen resumes with software (ATS) before a human reads them.")
        ats_ok = [l for l, ok in ats["checks"] if ok]
        if ats_ok:
            st.markdown("**✅ ATS-ready:** " + ", ".join(ats_ok))
        if ats["tips"]:
            st.markdown("**⚠️ Fix for ATS:**")
            for lbl, tip in ats["tips"]:
                st.markdown(f"- **{lbl}** — {tip}")
        if not ats["has_achievements"]:
            st.info("💡 Add **measurable achievements** with numbers — e.g. "
                    "'improved accuracy by 18%' or 'cut runtime 2x'.")
    else:
        st.info("Upload a resume in the sidebar (choose *Upload Resume*) to score it.")

    st.markdown("---")
    st.markdown('<div class="sec-label">📑 Compare two resume versions</div>',
                unsafe_allow_html=True)
    rc1, rc2 = st.columns(2)
    pa = rc1.file_uploader("Resume A", type=["pdf"], key="cmpA")
    pb = rc2.file_uploader("Resume B", type=["pdf"], key="cmpB")
    if pa and pb:
        ta, tb = extract_text_from_pdf(pa), extract_text_from_pdf(pb)
        sa = extract_skills(ta) if not ta.startswith("__ERROR__") else []
        sb = extract_skills(tb) if not tb.startswith("__ERROR__") else []
        ga, gb = analyze_gap(sa, target_role), analyze_gap(sb, target_role)
        qa, qb = score_resume_quality(ta), score_resume_quality(tb)
        rc1.metric("Resume A — match", f"{ga['match_percent']}%")
        rc1.metric("Resume A — quality", f"{qa['score']}/100")
        rc1.caption(f"{len(sa)} skills detected")
        rc2.metric("Resume B — match", f"{gb['match_percent']}%")
        rc2.metric("Resume B — quality", f"{qb['score']}/100")
        rc2.caption(f"{len(sb)} skills detected")
        winner = "A" if (ga['match_percent'] + qa['score']) >= (gb['match_percent'] + qb['score']) else "B"
        st.success(f"Overall, **Resume {winner}** is the stronger version for {target_role}.")

# ============================================================ TAB 6: JD MATCH
with tabs[6]:
    st.markdown('<div class="sec-label">Paste a real job description — score your resume '
                'against THAT specific job, not a generic role.</div>',
                unsafe_allow_html=True)
    if not student_skills:
        st.info("👈 Add your skills first (sidebar).")
    jd_text = st.text_area("Paste the job description here:", height=180,
                           placeholder="Paste the full JD text from LinkedIn/Naukri/company site…")
    if st.button("🎯 Match my skills to this job") and jd_text.strip():
        if not student_skills:
            st.warning("Add your skills in the sidebar first.")
        else:
            jm = jd_match(student_skills, jd_text)
            jd_skills = jm["jd_skills"]
            note = ""
            # AI fallback: some JDs are prose / competency language with no plain skill
            # keywords. If the fast matcher finds nothing, let Gemini parse the JD.
            if not jd_skills:
                ai_prompt = (
                    "From the job description below, extract the technical skills, tools "
                    "and technologies the candidate needs. Reply with ONLY a comma-separated "
                    "list of short skill names (e.g. Python, SQL, AWS, React). If it names NO "
                    "specific technical skills, reply with exactly: NONE.\n\n"
                    "JOB DESCRIPTION:\n" + jd_text)
                with st.spinner("🤖 Parsing this job description with AI…"):
                    ai_text, err = gemini_generate(ai_prompt)
                if err:
                    show_ai_error(err)
                elif ai_text:
                    ai_clean = ai_text.strip()
                    ai_known = [] if ai_clean.upper().startswith("NONE") else extract_skills(ai_clean)
                    if ai_known:
                        student_set = set(student_skills)
                        matched = [s for s in ai_known if s in student_set]
                        missing = [s for s in ai_known if s not in student_set]
                        jm = {"jd_skills": ai_known, "matched": matched, "missing": missing,
                              "match_percent": round(len(matched) / len(ai_known) * 100)}
                        jd_skills = ai_known
                        note = "🤖 AI parsed this JD — it didn't list skills as plain keywords."
                    else:
                        st.info("This job description is written in **general competency "
                                "language** — it doesn't name specific tools or technologies, "
                                "so there's no hard-skill match to compute. Paste a JD that "
                                "lists concrete tech (e.g. Python, React, AWS) for a skills match.")
                        if not ai_clean.upper().startswith("NONE"):
                            themes = ", ".join(t.strip() for t in ai_clean.split(",")[:8])
                            st.caption("AI-detected focus areas: " + (themes or ai_clean[:160]))
            if jd_skills:
                if note:
                    st.caption(note)
                st.markdown(f"### JD match: {jm['match_percent']}%")
                st.progress(jm["match_percent"] / 100)
                st.markdown('<div class="sec-label">✅ You match</div>', unsafe_allow_html=True)
                st.markdown(pills(jm["matched"], "pill-have"), unsafe_allow_html=True)
                st.markdown('<div class="sec-label">❌ This job wants (you\'re missing)</div>',
                            unsafe_allow_html=True)
                st.markdown(pills(jm["missing"], "pill-miss"), unsafe_allow_html=True)
                if ss.auth_user:
                    api_client.save_jd(ss.session, target_role, jm["match_percent"],
                                       jm["matched"], jm["missing"], jd_text)

# ============================================================ TAB 7: AI MENTOR
with tabs[7]:
    st.markdown('<div class="sec-label">💬 Ask your AI mentor about your roadmap, '
                'skills or career — it remembers the conversation.</div>',
                unsafe_allow_html=True)
    for m in ss.chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    q = st.chat_input("e.g. Which skill should I learn first? How do I start with LangChain?")
    if q:
        ss.chat.append({"role": "user", "content": q})
        if ss.auth_user:
            api_client.save_chat(ss.session, target_role, "user", q)
        with st.chat_message("user"):
            st.markdown(q)
        ctx = ""
        if result:
            ctx = (f"Context: the student targets {target_role}, is "
                   f"{result['match_percent']}% ready, and still needs: "
                   f"{', '.join(result['all_missing']) or 'nothing'}. ")
        hist = "\n".join(f"{m['role']}: {m['content']}" for m in ss.chat[-6:])
        prompt = ("You are SkillBridge's friendly, concise AI career mentor for an Indian "
                  "engineering student. " + ctx + "Answer their latest question in a few "
                  "short paragraphs or bullets.\n\n" + hist + "\nassistant:")
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                text, err = gemini_generate(prompt)
            if err:
                show_ai_error(err)
                ss.chat.pop()
            else:
                st.markdown(text)
                ss.chat.append({"role": "assistant", "content": text})
                if ss.auth_user:
                    api_client.save_chat(ss.session, target_role, "assistant", text)

# ---------------------------------------------------------------- MARKET PULSE (footer, AI optional)
st.markdown("---")
with st.expander("📈 Live job-market data for " + target_role):
    ranked, meta = cached_live_skills(target_role)
    if meta.get("source") == "adzuna":
        st.markdown(f"**🔴 LIVE — top skills from {meta.get('jobs', 0)} real Adzuna job "
                    f"ads in India:**")
        st.markdown(" ".join(f'<span class="pill pill-hot">{sk} · {n}</span>'
                             for sk, n in ranked), unsafe_allow_html=True)
    else:
        st.markdown("**Top in-demand skills (curated demand index):** " +
                    ", ".join(f"{sk} ({d})" for sk, d in ranked))
        st.caption("Add a free Adzuna API key (ADZUNA_APP_ID / ADZUNA_APP_KEY in "
                   ".streamlit/secrets.toml) to pull REAL live job postings here.")
    if st.button("🔮 AI market summary"):
        with st.spinner("Reading the job market…"):
            text, err = ai_market_pulse(target_role, API_KEY)
        if err:
            show_ai_error(err)
        else:
            ss.market_text = text
    if ss.market_text:
        st.markdown(ss.market_text)
    st.caption("Curated index is always-on; the AI pulse is an optional live read. "
               "We don't scrape job boards (ToS); this is the honest, deploy-safe version.")
