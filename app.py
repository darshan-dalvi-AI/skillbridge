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
import os
import hashlib
import streamlit.components.v1 as components

from roles_data import (
    ROLE_REQUIREMENTS, MASTER_SKILLS, ROLE_SALARY_IN,
    ROLE_BENCHMARK, DEFAULT_BENCHMARK,
    BRANCHES, ROLE_TO_BRANCH, SALARY_BAND_MULT,
)
from analyzer import (
    extract_text_from_pdf, extract_skills, analyze_gap,
    estimate_timeline, rank_in_demand, score_resume_quality, jd_match,
    ats_score, skill_categories, extract_experience,
)
from courses_data import get_courses
from market_data import curated_market, ai_market_pulse
from jobs_api import fetch_live_skills, match_live
from share_card import build_share_card
from report import build_report_pdf
import auth
import api_client
import semantic
import planner
import cover_letter

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
import seo
st.set_page_config(page_title=seo.TITLE,   # 50-60 chars, keyword-rich (SEO audit fix)
                   page_icon="🎯", layout="wide")
# Patch Streamlit's served index.html with meta description, canonical, Open
# Graph / X cards, JSON-LD schema and crawlable H1 content (SEO audit fixes).
seo.inject_seo()

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
ss.setdefault("resume_text", "")
ss.setdefault("semantic_on", True)
ss.theme = "light" if ss.get("theme_toggle", False) else "dark"

# ---------------------------------------------------------------- THEME / CSS
_VARS_DARK = """
:root{
 --bg-grad: radial-gradient(58vw 52vw at 8% -10%, rgba(255,106,44,0.22) 0%, transparent 60%),
            radial-gradient(55vw 52vw at 96% 2%, rgba(46,123,255,0.20) 0%, transparent 58%),
            linear-gradient(180deg,#080a12 0%,#05060c 100%);
 --text:#eef3fb; --sub:#8b98ad;
 --glass-bg:rgba(255,255,255,0.045); --glass-border:rgba(140,160,190,0.16);
 --have-bg:rgba(46,123,255,0.16); --have-fg:#7db4ff; --have-bd:rgba(46,123,255,0.46);
 --miss-bg:rgba(255,106,44,0.15); --miss-fg:#ffae7d; --miss-bd:rgba(255,106,44,0.46);
 --bonus-bg:rgba(167,139,250,0.14); --bonus-fg:#c4b5fd; --bonus-bd:rgba(167,139,250,0.40);
 --accent1:#ff6a2c; --accent2:#2e7bff;
 --sidebar-bg:linear-gradient(180deg,#0b1020 0%,#06070e 100%);
 --field-bg:rgba(6,9,18,0.60); --field-fg:#eef3fb; --field-bd:rgba(140,160,190,0.22); --icon-invert:invert(0);
}
"""
_VARS_LIGHT = """
:root{
 --bg-grad: radial-gradient(60vw 55vw at 8% -10%, rgba(255,106,44,0.10) 0%, transparent 60%),
            radial-gradient(55vw 52vw at 96% 2%, rgba(46,123,255,0.10) 0%, transparent 58%),
            linear-gradient(180deg,#f7f9fc 0%,#eef2f8 100%);
 --text:#0f1830; --sub:#516079;
 --glass-bg:rgba(255,255,255,0.82); --glass-border:rgba(15,23,42,0.10);
 --have-bg:rgba(37,99,235,0.12); --have-fg:#1d4ed8; --have-bd:rgba(37,99,235,0.38);
 --miss-bg:rgba(234,88,12,0.12); --miss-fg:#c2410c; --miss-bd:rgba(234,88,12,0.36);
 --bonus-bg:rgba(124,58,237,0.10); --bonus-fg:#6d28d9; --bonus-bd:rgba(124,58,237,0.30);
 --accent1:#ea580c; --accent2:#2563eb;
 --sidebar-bg:linear-gradient(180deg,#eef2f8 0%,#e3e9f3 100%);
 --field-bg:#ffffff; --field-fg:#0f1830; --field-bd:#cbd5e1; --icon-invert:invert(1);
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
.hero-wrap{ text-align:center; padding:26px 12px 8px; margin:2px 0 6px; position:relative;
  background:radial-gradient(58% 135% at 50% 32%, rgba(5,7,14,.58), transparent 72%); }
.hero-title{ font-family:'Space Grotesk',sans-serif; font-size:clamp(2.9rem,6.6vw,4.9rem) !important; font-weight:700;
  text-align:center; background:linear-gradient(110deg,#ff6a2c,#ff9a4d 38%,#5aa0ff);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
  margin:18px 0 0; letter-spacing:-0.02em; line-height:1.02;
  filter:drop-shadow(0 4px 30px rgba(0,0,0,.65)) drop-shadow(0 6px 40px rgba(255,106,44,.5));}
.hero-sub{ text-align:center; color:#aab6c9 !important; font-family:'DM Sans'; font-size:1.0rem !important;
  letter-spacing:4px; text-transform:uppercase; margin:10px 0 14px; font-weight:600;}
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
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong, [data-testid="stMarkdownContainer"] b,
[data-testid="stMarkdownContainer"] em, [data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th{ color:var(--text) !important; }
.sec-label{ font-family:'Space Grotesk'; font-weight:600; color:var(--text); font-size:1.0rem;
  margin:14px 0 8px; letter-spacing:-0.01em;}
.stButton>button{ background:linear-gradient(135deg,#ff6e33,#ff8a3d);
  color:#1b0f06; border:0; border-radius:12px; font-family:'DM Sans'; font-weight:700;
  padding:9px 20px; transition:transform .15s,box-shadow .2s;
  box-shadow:0 10px 26px -12px rgba(255,106,44,.8);}
.stButton>button:hover{ transform:translateY(-1px); box-shadow:0 14px 32px -12px rgba(255,106,44,.95);}
.stButton>button:active{ transform:translateY(1px);}
[data-testid="stSidebar"]{ background:var(--sidebar-bg) !important; border-right:1px solid var(--glass-border);}
.stProgress > div > div > div{ background:linear-gradient(90deg,#ff6a2c,#2e7bff) !important; }
.stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"] p { color:var(--sub); font-weight:600; }
.stTabs [data-baseweb="tab"][aria-selected="true"], .stTabs [data-baseweb="tab"][aria-selected="true"] p { color:var(--text); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"]{ background:linear-gradient(90deg,#ff6a2c,#2e7bff) !important; }
/* GLOWING BOX on the active tab — bigger & cooler so you always know which feature is open */
.stTabs [data-baseweb="tab-list"]{ gap:7px; }
.stTabs [data-baseweb="tab"]{ border-radius:14px; padding:10px 20px !important;
  transition:background .25s, box-shadow .25s, color .25s, transform .25s; }
.stTabs [data-baseweb="tab"]:hover{ background:rgba(148,163,184,0.12); }
.stTabs [data-baseweb="tab"][aria-selected="true"]{
  background:linear-gradient(135deg, rgba(255,106,44,0.26), rgba(46,123,255,0.14)) !important;
  transform:translateY(-1px); animation:tabGlow 2.4s ease-in-out infinite; }
@keyframes tabGlow{
  0%,100%{ box-shadow:inset 0 0 0 1.7px rgba(255,106,44,0.62), 0 0 24px rgba(255,106,44,0.42), 0 0 50px rgba(255,106,44,0.20); }
  50%{ box-shadow:inset 0 0 0 1.7px rgba(255,106,44,0.9), 0 0 38px rgba(255,106,44,0.65), 0 0 72px rgba(255,106,44,0.32); } }
@media(prefers-reduced-motion:reduce){ .stTabs [data-baseweb="tab"][aria-selected="true"]{ animation:none;
  box-shadow:inset 0 0 0 1.7px rgba(255,106,44,0.7), 0 0 30px rgba(255,106,44,0.5) !important; } }
.stTabs [data-baseweb="tab"][aria-selected="true"] p,
.stTabs [data-baseweb="tab"][aria-selected="true"]{ color:var(--text) !important; font-weight:700 !important; }
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
.stButton>button{ color:#1b0f06 !important; }
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
/* ---------------- Fusion AI polish ---------------- */
.glass{ transition:transform .25s ease, box-shadow .25s ease;
  box-shadow:0 20px 55px -34px rgba(46,123,255,.55), inset 0 1px 0 rgba(255,255,255,.04); }
.glass:hover{ transform:translateY(-2px);
  box-shadow:0 28px 66px -30px rgba(255,106,44,.42), inset 0 1px 0 rgba(255,255,255,.06); }
.stButton>button{ position:relative; overflow:hidden; letter-spacing:.2px; }
.stButton>button:hover{ box-shadow:0 16px 40px -12px rgba(255,138,61,.85), 0 0 22px rgba(46,123,255,.35); }
[data-testid="stChatInput"] > div{ box-shadow:0 0 0 1px rgba(255,106,44,.35),
  0 0 26px -6px rgba(46,123,255,.45); animation:chatGlow 3.4s ease-in-out infinite; }
@keyframes chatGlow{ 0%,100%{ box-shadow:0 0 0 1px rgba(255,106,44,.30), 0 0 22px -8px rgba(46,123,255,.40);}
  50%{ box-shadow:0 0 0 1px rgba(46,123,255,.45), 0 0 30px -4px rgba(255,106,44,.50);} }
@media(prefers-reduced-motion:reduce){ [data-testid="stChatInput"] > div{ animation:none; } }
/* multiselect skill chips -> legible blue chips (skills you know = blue) */
[data-baseweb="tag"]{ background:linear-gradient(135deg,#2e7bff,#1e6bff) !important;
  border:0 !important; color:#ffffff !important; border-radius:9px !important;
  box-shadow:0 4px 14px -7px rgba(46,123,255,.85) !important; }
[data-baseweb="tag"] span, [data-baseweb="tag"] div, [data-baseweb="tag"] *{ color:#ffffff !important; }
[data-baseweb="tag"] svg{ fill:#ffffff !important; color:#ffffff !important; }
[data-baseweb="tag"] [role="presentation"]:hover, [data-baseweb="tag"] [role="button"]:hover{
  background:rgba(255,255,255,.22) !important; border-radius:6px; }
/* AI Mentor: make the "you" (user) avatar blue to match the theme (assistant stays orange) */
[data-testid="stChatMessageAvatarUser"]{ background:linear-gradient(135deg,#2e7bff,#1e6bff) !important;
  color:#ffffff !important; border:0 !important; }
[data-testid="stChatMessageAvatarUser"] svg{ fill:#ffffff !important; color:#ffffff !important; }
/* ---- immersive full-page 3D backdrop (the website look) ---- */
html, body{ background:var(--bg-grad) !important; background-attachment:fixed !important; }
.stApp{ background:transparent !important; }
[data-testid="stAppViewContainer"], [data-testid="stMain"], section.main,
[data-testid="stMainBlockContainer"], [data-testid="stBottomBlockContainer"]{ background:transparent !important; }
iframe[title="st.iframe"]{ position:fixed !important; top:0 !important; left:0 !important;
  width:100vw !important; height:100vh !important; border:0 !important; margin:0 !important;
  z-index:-1 !important; pointer-events:none !important; }
"""


def inject_theme():
    vars_block = _VARS_LIGHT if ss.theme == "light" else _VARS_DARK
    st.markdown("<style>" + vars_block + _BASE_CSS + "</style>", unsafe_allow_html=True)


inject_theme()
CHART_FONT = "#16202e" if ss.theme == "light" else "#e6eef8"

def _theme_fig(fig):
    """Force legible, theme-aware axis text + soft gridlines + auto-margins (no clipping)."""
    grid = "rgba(148,163,184,0.16)" if ss.theme == "dark" else "rgba(15,23,42,0.12)"
    fig.update_layout(font=dict(color=CHART_FONT),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(tickfont=dict(color=CHART_FONT), title_font=dict(color=CHART_FONT),
                     gridcolor=grid, zerolinecolor=grid, linecolor=grid, automargin=True)
    fig.update_yaxes(tickfont=dict(color=CHART_FONT), title_font=dict(color=CHART_FONT),
                     gridcolor=grid, zerolinecolor=grid, linecolor=grid, automargin=True)
    return fig
# Hide Plotly's hover toolbar (zoom/pan/reset are no-ops on pie/radar and
# unreliable on touch); charts stay clean and still show hover tooltips.
_PLOTLY_CFG = {"displayModeBar": False}

# ---------------------------------------------------------------- AI (OpenRouter)
import time
import llm


def _ai_is_transient(err: str) -> bool:
    e = (err or "").lower()
    return any(k in e for k in ("503", "500", "unavailable", "overload",
                                "high demand", "internal", "try again",
                                "deadline", "timeout", "429", "resource_exhausted"))


def gemini_generate(prompt: str, model: str = None):
    """Generate text for every AI feature. Routes through OpenRouter (llm.chat),
    which retries and falls back across models. (Function name kept so the many
    existing call-sites don't need to change.)"""
    return llm.chat(prompt, model=model)


def show_ai_error(err: str):
    e = err or ""
    el = e.lower()
    if err == "no_key":
        st.info("**Add your OpenRouter API key** to use AI features "
                "(`.streamlit/secrets.toml` → `OPENROUTER_API_KEY`).")
    elif "402" in e or "payment" in el or "credit" in el:
        st.warning("💳 Your OpenRouter account is out of credits. Add credits at "
                   "openrouter.ai to re-enable the AI features.")
    elif "401" in e or "invalid api key" in el:
        st.error("🔑 The OpenRouter API key looks invalid — check `OPENROUTER_API_KEY` "
                 "in your secrets.")
    elif "429" in e or "rate limit" in el:
        st.warning("⏳ Rate-limited right now. Please wait ~30 seconds and try again.")
    elif _ai_is_transient(e):
        st.warning("🌐 The AI model is busy right now. I already tried a backup model "
                   "automatically — wait a few seconds and try again. Your data is safe.")
    else:
        st.error(f"Something went wrong: {err}")


def pills(skills, cls):
    if not skills:
        return "_None_"
    return " ".join(f'<span class="pill {cls}">{s}</span>' for s in skills)


def _login_form():
    """Email / password sign-in (backend, with local fallback)."""
    _mode = st.radio("Account", ["Log in", "Register"], horizontal=True,
                     label_visibility="collapsed", key="auth_mode")
    _u = st.text_input("Username", key="auth_u")
    _p = st.text_input("Password", type="password", key="auth_p")
    if st.button(_mode, key="auth_submit"):
        ok, msg, sess = (api_client.register(_u, _p) if _mode == "Register"
                         else api_client.authenticate(_u, _p))
        if ok:
            ss.auth_user = sess["username"]; ss.session = sess
            ss.learned = api_client.get_progress(sess, ss.auth_user).get("learned", [])
            st.rerun()
        else:
            st.error(msg)


@st.cache_data(ttl=1800, show_spinner="Pulling live job-market data…")
def cached_live_skills(role):
    """Cache live job-market fetch per role (30 min) so Adzuna isn't hit on
    every rerun and the demo stays snappy."""
    return fetch_live_skills(role)


@st.cache_data(ttl=3600, show_spinner="🧠 Inferring related skills…")
def cached_semantic_skills(resume_text, already_tuple):
    """Semantic (embedding/RAG) skill inference, cached by résumé text so the
    Gemini embedding call runs once per unique résumé — reruns stay free.
    Returns (added_skills, meta); ([], …) whenever the index or key is missing."""
    return semantic.infer_skills(resume_text, list(already_tuple))


@st.cache_data(ttl=60, show_spinner=False)
def cached_history(_session, key):
    """Cache the user's progress history (a backend HTTP GET) for 60s so the
    Progress tab doesn't re-hit the API on every Streamlit rerun. `key` (the
    user id / name) keeps users' caches separate; `_session` is not hashed.
    Cleared right after a save so the chart always shows the latest point."""
    return api_client.get_history(_session)


@st.cache_data(ttl=60, show_spinner=False)
def cached_export(_session, key):
    """Cache the user's full data export (a backend HTTP GET) for 60s so the
    Progress tab doesn't re-hit the API on every rerun. Keyed per user; cleared
    on save so the JSON download reflects the latest state."""
    return api_client.export_all(_session)


# ------------------------------------------------------- RESTORE ON REFRESH
def _restore_profile_once():
    """On a fresh load, pull the signed-in user's saved profile back from the backend
    so a refresh does not wipe their skills / role / resume. (Google sessions persist
    across refresh via cookie; email/password sessions restore on next login.)"""
    if ss.get("_restored"):
        return
    try:
        _gauth = "auth" in st.secrets
    except Exception:
        _gauth = False
    _gu = getattr(st, "user", None)
    if _gauth and _gu is not None and getattr(_gu, "is_logged_in", False) and not ss.auth_user:
        _em = (getattr(st.user, "email", "") or "").strip().lower()
        if _em:
            _pw = hashlib.sha256(("skbridge-oauth::" + _em).encode()).hexdigest()[:24]
            ok, _m, sess = api_client.authenticate(_em, _pw)
            if not ok:
                ok, _m, sess = api_client.register(_em, _pw)
            if ok:
                ss.auth_user = sess["username"]; ss.session = sess
    if ss.auth_user and api_client.is_api(ss.session):
        prof = getattr(api_client, "get_profile", lambda *a, **k: {})(ss.session) or {}
        _sk = [s for s in (prof.get("skills") or []) if s in MASTER_SKILLS]
        if _sk:
            ss.setdefault("manual_skills", _sk)
            ss.setdefault("skill_method", "✅ Select Skills Manually")
            ss["_restored_skills"] = _sk
        if prof.get("target_role") in ROLE_REQUIREMENTS:
            ss.setdefault("role_sel", prof["target_role"])
            ss.setdefault("branch_sel", ROLE_TO_BRANCH.get(prof["target_role"], "Computer / IT"))
        if prof.get("resume_text"):
            ss.resume_text = prof["resume_text"]
            ss.setdefault("resumes", [])
            if not ss.resumes:
                ss.resumes = [{"name": "Saved résumé", "text": prof["resume_text"]}]
        ss.learned = getattr(api_client, "get_progress", lambda *a, **k: {})(ss.session, ss.auth_user).get("learned", [])
        ss["_restored"] = True


_restore_profile_once()


# ---------------------------------------------------------------- SIDEBAR
with st.sidebar:
    top_box = st.container()  # account + theme show here (visually first)

    # ---- data actions run BEFORE the inputs so widget keys reset safely ----
    if ss.pop("_do_clear_resume", False):
        ss.pop("resume_paste", None)
        ss.pop("main_resume", None)
        ss.resumes = []
        ss._last_pdf_n = None
        ss._pdf_key = ss.get("_pdf_key", 0) + 1     # fresh picker instance
        ss.resume_text = ""
        if ss.auth_user and api_client.is_api(ss.session):
            try:
                api_client.save_profile(ss.session, ss.get("role_sel", ""),
                                        ss.get("student_skills", []), "")
            except Exception:
                pass
        st.toast("Résumés removed — add a new one anytime.", icon=":material/delete:")
    if ss.pop("_do_clear_all", False):
        if ss.auth_user and api_client.is_api(ss.session):
            try:
                api_client.save_profile(ss.session, "", [], "")
                api_client.save_progress(ss.session, ss.auth_user, "", 0, [])
            except Exception:
                pass
        for _k in ("resume_paste", "main_resume", "manual_skills", "skill_method",
                   "role_sel", "_restored_skills", "student_skills",
                   "_last_saved_sig", "confirm_clear_all"):
            ss.pop(_k, None)
        for _k in ("roadmap_text", "projects_text", "interview_text", "market_text"):
            ss[_k] = ""
        ss.resumes = []
        ss._last_pdf_n = None
        ss._pdf_key = ss.get("_pdf_key", 0) + 1
        ss.resume_text = ""
        ss.chat = []
        ss.learned = []
        ss["_restored"] = True            # keep restore OFF so an in-session rerun can't re-load wiped data
        st.toast("🧹 Cleared everything — fresh start.")

    # Skills & role are instantiated FIRST so the login/logout reruns in the
    # account box below can never discard the user's selected skills.
    st.markdown("### 🎯 Your Target")
    branch = st.selectbox("Your branch / stream:", list(BRANCHES.keys()), key="branch_sel")
    _role_opts = BRANCHES[branch]
    if ss.get("role_sel") not in _role_opts:
        ss["role_sel"] = _role_opts[0]
    target_role = st.selectbox("Target role you want:", _role_opts, key="role_sel")
    method = st.radio("How to provide your skills:",
                      ["📄 Upload Resume (PDF)", "📋 Paste Resume Text",
                       "✅ Select Skills Manually"], key="skill_method")

    resume_text = ""
    base_skills = []
    if method == "📄 Upload Resume (PDF)":
        ss.setdefault("resumes", [])
        ss.setdefault("_last_pdf_n", None)
        ss.setdefault("_pdf_key", 0)
        if _pdf_reader is not None:
            st.caption("Pick your PDF below — it is read **on your device** "
                       "(nothing is uploaded), so it works on phones too. "
                       "You can add more than one.")
            raw = _pdf_reader(key=f"pdf_reader_{ss._pdf_key}", default=None, theme=ss.theme)
            cur_n = raw.get("n") if isinstance(raw, dict) else None
            if isinstance(raw, dict) and (raw.get("text") or "").strip() and cur_n != ss._last_pdf_n:
                ss._last_pdf_n = cur_n
                _nm = (raw.get("name") or "Résumé").strip()
                _txt = raw["text"].strip()
                if not any(r["text"] == _txt for r in ss.resumes):
                    ss.resumes.append({"name": _nm, "text": _txt})
            with st.expander("Trouble picking a file? Use the classic uploader"):
                _up = st.file_uploader("Upload your resume", type=["pdf"], key="main_resume")
                if _up:
                    _t = extract_text_from_pdf(_up)
                    if (not _t.startswith("__ERROR__")) and _t.strip() and \
                            not any(r["text"] == _t.strip() for r in ss.resumes):
                        ss.resumes.append({"name": _up.name, "text": _t.strip()})
        else:
            _up = st.file_uploader("Upload your resume", type=["pdf"], key="main_resume")
            if _up:
                _t = extract_text_from_pdf(_up)
                if (not _t.startswith("__ERROR__")) and _t.strip() and \
                        not any(r["text"] == _t.strip() for r in ss.resumes):
                    ss.resumes.append({"name": _up.name, "text": _t.strip()})
        if ss.resumes:
            st.markdown("**Your résumés** — tap :material/delete: to remove just that one:")
            for _i, _r in enumerate(list(ss.resumes)):
                _c1, _c2 = st.columns([0.8, 0.2])
                _c1.markdown(f"📄 {_r['name']}")
                if _c2.button(":material/delete:", key=f"del_resume_{_i}", help=f"Remove {_r['name']}"):
                    ss.resumes.pop(_i)
                    st.rerun()
            resume_text = "\n\n".join(r["text"] for r in ss.resumes)
            base_skills = extract_skills(resume_text)
            st.success(f"Found {len(base_skills)} skills across {len(ss.resumes)} résumé(s).")
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

    if not base_skills and ss.get("_restored_skills"):
        base_skills = ss["_restored_skills"]

    # ---- optional semantic (embedding/RAG) skill inference --------------------
    # When a résumé's TEXT is available and a precomputed index exists, also infer
    # skills the résumé implies but never names outright. Silent no-op without the
    # index or an API key, so the keyword result is always the safe baseline.
    _sem_added = []
    _sem_text = (resume_text or "").strip()
    if _sem_text and semantic.index_exists():
        if st.toggle("🧠 Smart semantic detection", key="semantic_on",
                     help="Also infer skills your résumé implies but doesn't spell out "
                          "(embeddings / RAG). Turn off for pure keyword matching."):
            _inferred, _sem_meta = cached_semantic_skills(_sem_text, tuple(base_skills))
            if _inferred:
                # let the user untick anything wrongly inferred (accept/reject)
                _acc_key = "sem_acc_" + hashlib.md5(_sem_text.encode("utf-8")).hexdigest()[:8]
                st.caption("🧠 Inferred from your résumé — untick any you don't actually have:")
                _sem_added = st.multiselect("Inferred skills", _inferred, default=_inferred,
                                            key=_acc_key, label_visibility="collapsed")
                if _sem_added:
                    base_skills = sorted(set(base_skills) | set(_sem_added))
    ss["semantic_added"] = _sem_added

    ss.student_skills = base_skills
    if ss.get("_restored_skills") and ss.auth_user:
        st.caption("↩️ Restored your saved profile — change any input to update it.")
    # keep the last real résumé so it survives method-switches & refresh;
    # the "Remove résumé" button is the only way to clear it
    if (resume_text or "").strip():
        ss.resume_text = resume_text

    with st.expander("⚙️ Manage my data"):
        _nres = len(ss.get("resumes", []))
        if _nres or (ss.get("resume_text") or "").strip():
            _lbl = (f"{_nres} résumé(s)" if _nres else "résumé text")
            st.caption(f"📄 {_lbl} on file.")
            if st.button("Remove all résumés", icon=":material/delete:", use_container_width=True, key="rm_resume_btn"):
                ss["_do_clear_resume"] = True
                st.rerun()
            st.caption("Or delete them one-by-one with the :material/delete: next to each résumé above.")
        else:
            st.caption("No résumé on file yet — upload or paste one above.")
        st.markdown("<hr style='margin:8px 0;border:0;border-top:1px solid "
                    "rgba(148,163,184,.25)'>", unsafe_allow_html=True)
        _sure = st.checkbox("Yes, wipe everything", key="confirm_clear_all")
        if st.button("🧹 Clear all my data & chat", use_container_width=True,
                     disabled=not _sure, key="clear_all_btn"):
            ss["_do_clear_all"] = True
            st.rerun()
        st.caption("Clears your skills, résumé, analysis, AI-mentor chat and your "
                   "saved profile — a clean start.")
    st.caption("Built by Darshan Dalvi · Final-year B.E. Project\n\n"
               "Python · NLP · Gemini · Streamlit · Plotly")

    with top_box:
        st.markdown("### 👤 Account")
        try:
            _auth_on = "auth" in st.secrets
        except Exception:
            _auth_on = False
        _gu = getattr(st, "user", None)
        _g_in = bool(_auth_on and _gu is not None and getattr(_gu, "is_logged_in", False))

        if _g_in:
            if not ss.auth_user:
                _em = (getattr(st.user, "email", "") or "").strip().lower()
                _pw = hashlib.sha256(("skbridge-oauth::" + _em).encode()).hexdigest()[:24]
                ok, _m, sess = api_client.authenticate(_em, _pw)
                if not ok:
                    ok, _m, sess = api_client.register(_em, _pw)
                if ok:
                    ss.auth_user = sess["username"]; ss.session = sess
                    ss.learned = api_client.get_progress(sess, ss.auth_user).get("learned", [])
            _pic = getattr(st.user, "picture", None)
            if _pic:
                st.markdown(f'<img src="{_pic}" style="width:48px;height:48px;'
                            'border-radius:50%;border:2px solid #22c55e;margin-bottom:6px">',
                            unsafe_allow_html=True)
            st.success(f"Signed in as **{getattr(st.user, 'name', None) or ss.auth_user}**")
            _store = "☁️ Backend" if api_client.is_api(ss.session) else "💾 Local"
            st.caption(f"Saving to: {_store} · {getattr(st.user, 'email', '')}")
            if st.button("Sign out"):
                ss.auth_user = None; ss.session = None; ss.learned = []; ss.chat = []
                ss.pop("_last_saved_sig", None); st.logout()
        elif ss.auth_user:
            st.success(f"Logged in as **{ss.auth_user}**")
            _store = "☁️ Backend" if api_client.is_api(ss.session) else "💾 Local (backend offline)"
            st.caption(f"Saving to: {_store}")
            if st.button("Log out"):
                ss.auth_user = None; ss.session = None; ss.learned = []; ss.chat = []
                ss.pop("_last_saved_sig", None); st.rerun()
        else:
            if _auth_on:
                if st.button("Sign in with Google", use_container_width=True):
                    st.login()
                st.caption("Sign in to save your roadmap & progress across devices.")
                with st.expander("or use email / password"):
                    _login_form()
            else:
                _login_form()
                st.caption("Login saves your data to the SkillBridge backend "
                           "(falls back to local storage if it isn't running).")
        st.markdown("---")
        _theme_label = "☀️ Light mode" if ss.theme == "light" else "🌙 Dark mode"
        st.toggle(_theme_label, key="theme_toggle")
        st.markdown("---")

# ---------------------------------------------------------------- HEADER
_BG3D = r"""<canvas id="sbbg"></canvas>
<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}#sbbg{display:block;width:100vw;height:100vh}</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  try{ var _fe=window.frameElement; if(_fe){ _fe.style.cssText="position:fixed;top:0;left:0;width:100vw;height:100vh;border:0;margin:0;z-index:-1;pointer-events:none;"; var _w=_fe.parentElement; for(var _k=0;_k<3&&_w;_k++){_w.style.height="0";_w.style.minHeight="0";_w=_w.parentElement;} } }catch(e){}
  if(typeof THREE==='undefined')return;
  var cv=document.getElementById('sbbg');
  function vp(){return [window.innerWidth||1200, window.innerHeight||800];}
  var v=vp(),W=v[0],H=v[1];
  var rnd=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true});
  rnd.setPixelRatio(Math.min(devicePixelRatio||1,2)); rnd.setSize(W,H,false);
  var scene=new THREE.Scene();
  var cam=new THREE.PerspectiveCamera(62,W/H,0.1,260); cam.position.z=18;
  var cA=new THREE.Color(0xff7a36), cB=new THREE.Color(0x4a9bff);
  // deep parallax starfield
  var SN=(W<680?260:560), sp=new Float32Array(SN*3), sc=new Float32Array(SN*3);
  for(var i=0;i<SN;i++){ sp[i*3]=(Math.random()-.5)*72; sp[i*3+1]=(Math.random()-.5)*48; sp[i*3+2]=(Math.random()-.5)*60-12;
    var c=Math.random()<.5?cA:cB; sc[i*3]=c.r;sc[i*3+1]=c.g;sc[i*3+2]=c.b; }
  var sg=new THREE.BufferGeometry();
  sg.setAttribute('position',new THREE.BufferAttribute(sp,3));
  sg.setAttribute('color',new THREE.BufferAttribute(sc,3));
  var stars=new THREE.Points(sg,new THREE.PointsMaterial({size:.16,vertexColors:true,transparent:true,opacity:.72,blending:THREE.AdditiveBlending,depthWrite:false}));
  scene.add(stars);
  // living constellation network
  var NN=(W<680?70:130), BX=20,BY=13,BZ=8;
  var np=new Float32Array(NN*3), ncol=new Float32Array(NN*3), nv=new Float32Array(NN*3);
  for(var i=0;i<NN;i++){ np[i*3]=(Math.random()-.5)*2*BX; np[i*3+1]=(Math.random()-.5)*2*BY; np[i*3+2]=(Math.random()-.5)*2*BZ;
    var c=Math.random()<.5?cA:cB; ncol[i*3]=c.r;ncol[i*3+1]=c.g;ncol[i*3+2]=c.b;
    nv[i*3]=(Math.random()-.5)*.022; nv[i*3+1]=(Math.random()-.5)*.022; nv[i*3+2]=(Math.random()-.5)*.015; }
  var ng=new THREE.BufferGeometry();
  ng.setAttribute('position',new THREE.BufferAttribute(np,3));
  ng.setAttribute('color',new THREE.BufferAttribute(ncol,3));
  var nodes=new THREE.Points(ng,new THREE.PointsMaterial({size:.30,vertexColors:true,transparent:true,opacity:.95,blending:THREE.AdditiveBlending,depthWrite:false}));
  scene.add(nodes);
  var MAXE=NN*7, ep=new Float32Array(MAXE*6), ec=new Float32Array(MAXE*6);
  var eg=new THREE.BufferGeometry();
  eg.setAttribute('position',new THREE.BufferAttribute(ep,3));
  eg.setAttribute('color',new THREE.BufferAttribute(ec,3));
  var edges=new THREE.LineSegments(eg,new THREE.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.55,blending:THREE.AdditiveBlending,depthWrite:false}));
  scene.add(edges);
  var DTH=5.0, DTH2=DTH*DTH;
  function step(){
    for(var i=0;i<NN;i++){ var x=i*3;
      np[x]+=nv[x]; np[x+1]+=nv[x+1]; np[x+2]+=nv[x+2];
      if(np[x]>BX||np[x]<-BX)nv[x]*=-1;
      if(np[x+1]>BY||np[x+1]<-BY)nv[x+1]*=-1;
      if(np[x+2]>BZ||np[x+2]<-BZ)nv[x+2]*=-1; }
    ng.attributes.position.needsUpdate=true;
    var e=0;
    for(var a=0;a<NN;a++){ var ax=a*3;
      for(var b=a+1;b<NN;b++){ var bx=b*3;
        var dx=np[ax]-np[bx],dy=np[ax+1]-np[bx+1],dz=np[ax+2]-np[bx+2];
        var d2=dx*dx+dy*dy+dz*dz;
        if(d2<DTH2 && e<MAXE){ var t=1-Math.sqrt(d2)/DTH, o=e*6;
          ep[o]=np[ax];ep[o+1]=np[ax+1];ep[o+2]=np[ax+2];
          ep[o+3]=np[bx];ep[o+4]=np[bx+1];ep[o+5]=np[bx+2];
          ec[o]=ncol[ax]*t;ec[o+1]=ncol[ax+1]*t;ec[o+2]=ncol[ax+2]*t;
          ec[o+3]=ncol[bx]*t;ec[o+4]=ncol[bx+1]*t;ec[o+5]=ncol[bx+2]*t;
          e++; } } }
    eg.setDrawRange(0,e*2); eg.attributes.position.needsUpdate=true; eg.attributes.color.needsUpdate=true;
  }
  var tx=0,ty=0,mx=0,my=0;
  try{ var P=window.parent; P.addEventListener('mousemove',function(ev){tx=(ev.clientX/(P.innerWidth||W)-.5);ty=(ev.clientY/(P.innerHeight||H)-.5);}); }catch(e){}
  function loop(){
    step();
    stars.rotation.y+=.00035; stars.rotation.x+=.00012;
    nodes.rotation.y+=.0006; edges.rotation.y+=.0006;
    nodes.rotation.x+=.0002; edges.rotation.x+=.0002;
    mx+=(tx-mx)*.04; my+=(ty-my)*.04;
    cam.position.x=mx*4.5; cam.position.y=-my*3.0; cam.lookAt(0,0,0);
    rnd.render(scene,cam); requestAnimationFrame(loop);
  }
  loop();
  function onresize(){var q=vp();W=q[0];H=q[1];cam.aspect=W/H;cam.updateProjectionMatrix();rnd.setSize(W,H,false);}
  addEventListener('resize',onresize);
  [120,400,900,1600,2600].forEach(function(ms){setTimeout(onresize,ms);});
})();
</script>"""
try:
    components.html(_BG3D, height=0, scrolling=False)   # fixed full-page 3D backdrop
except Exception:
    pass
# Real H1/H2 tags (same look — CSS targets the classes) so search engines see
# proper page headings instead of plain <p> text.
st.markdown('<h1 class="hero-title">SkillBridge</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="hero-sub">AI CAREER GUIDANCE · SKILL-GAP ANALYZER</h2>', unsafe_allow_html=True)

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
                marker_colors=["#3b82f6", "#ff7a36"]))
            fig.update_layout(height=210, margin=dict(t=10, b=10, l=10, r=10),
                              paper_bgcolor="rgba(0,0,0,0)", font_color=CHART_FONT,
                              showlegend=True, legend=dict(orientation="h", y=-0.1))
            st.plotly_chart(_theme_fig(fig), width="stretch", theme=None, config=_PLOTLY_CFG)
        with c3:
            sal = ROLE_SALARY_IN.get(target_role)
            if sal:
                _exp = extract_experience(ss.get("resume_text", ""))
                _lvl = _exp["level"]
                _mm = {b.split(" (")[0]: m for b, m in SALARY_BAND_MULT}
                _m = _mm.get(_lvl, 1.0)
                _lo, _hi = round(sal["low"] * _m, 1), round(sal["high"] * _m, 1)
                st.markdown('<div class="sec-label">💰 Salary by experience (India)</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="salary">₹{_lo}–{_hi} LPA</div>', unsafe_allow_html=True)
                if _exp["years"] > 0:
                    st.caption(f"~{_exp['years']} yrs experience detected in your résumé → "
                               f"**{_lvl}-level** market value · indicative, varies by company/city/skills.")
                else:
                    st.caption("Fresher band shown · upload a résumé with experience to see your "
                               "level & market value · indicative.")
                _rows = ""
                for _b, _mu in SALARY_BAND_MULT:
                    _blo, _bhi = round(sal["low"] * _mu, 1), round(sal["high"] * _mu, 1)
                    _here = _b.startswith(_lvl)
                    _style = ("font-weight:700;color:var(--have-fg)" if _here else "color:var(--sub)")
                    _rows += (f"<div style='display:flex;justify-content:space-between;gap:10px;"
                              f"padding:3px 0;{_style}'><span>{'▸ ' if _here else ''}{_b}</span>"
                              f"<span>₹{_blo}–{_bhi} LPA</span></div>")
                st.markdown(f"<div style='margin-top:6px;font-size:.85rem'>{_rows}</div>",
                            unsafe_allow_html=True)

        st.progress(result["match_percent"] / 100)

        st.markdown('<div class="sec-label">✅ Skills you already have</div>',
                    unsafe_allow_html=True)
        st.markdown(pills(result["matched_core"] + result["matched_bonus"], "pill-have"),
                    unsafe_allow_html=True)
        _sem_hit = [s for s in ss.get("semantic_added", [])
                    if s in (result["matched_core"] + result["matched_bonus"])]
        if _sem_hit:
            st.caption("🧠 Inferred semantically from your résumé (not named outright): "
                       + ", ".join(_sem_hit))

        # Skills in demand (bar) + badges
        st.markdown('<div class="sec-label">🔥 Missing skills — ranked by employer '
                    'demand</div>', unsafe_allow_html=True)
        ranked = rank_in_demand(result["all_missing"])
        if ranked:
            top = ranked[:10]
            fig2 = go.Figure(go.Bar(
                x=[s for s, _, _ in top], y=[d for _, d, _ in top],
                marker_color=["#ff8a3d" if hi else "#5b83ff" for _, _, hi in top]))
            fig2.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               font_color=CHART_FONT, yaxis_title="Demand score")
            st.plotly_chart(_theme_fig(fig2), width="stretch", theme=None, config=_PLOTLY_CFG)
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
            orientation="h", marker_color=["#3b82f6", "#9aa7bd"]))
        figp.update_layout(height=160, margin=dict(t=6, b=6, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT, xaxis_title="Match %", xaxis_range=[0, 100])
        st.plotly_chart(_theme_fig(figp), width="stretch", theme=None, config=_PLOTLY_CFG)
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
                line_color="#3b82f6", fillcolor="rgba(59,130,246,0.22)"))
            figr.update_layout(height=330, margin=dict(t=30, b=20, l=50, r=50),
                               paper_bgcolor="rgba(0,0,0,0)", font_color=CHART_FONT,
                               polar=dict(bgcolor="rgba(0,0,0,0)",
                                          radialaxis=dict(range=[0, 100],
                                              tickfont=dict(color=CHART_FONT)),
                                          angularaxis=dict(tickfont=dict(color=CHART_FONT))))
            st.plotly_chart(_theme_fig(figr), width="stretch", theme=None, config=_PLOTLY_CFG)
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
            marker_color=["#3b82f6" if sk in haveset else "#ff7a36" for sk, _ in top],
            text=["✓" if sk in haveset else "✗" for sk, _ in top], textposition="outside"))
        figL.update_layout(height=330, margin=dict(t=26, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT,
                           yaxis_title=("mentions in real jobs" if suffix == " jobs" else "demand"))
        st.plotly_chart(_theme_fig(figL), width="stretch", theme=None, config=_PLOTLY_CFG)
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
            # ---- Week-by-week study plan + calendar (.ics) export ----
            st.markdown('<div class="sec-label">📅 Your week-by-week study plan</div>',
                        unsafe_allow_html=True)
            _hpw = st.slider("Study hours per week", 3, 30, 10, key="plan_hpw")
            _weeks = planner.build_weekly_plan(timeline["per_skill"], hours_per_week=_hpw)
            st.markdown(planner.plan_to_markdown(_weeks))
            try:
                _ics = planner.plan_to_ics(_weeks, title=f"SkillBridge — {target_role}")
                st.download_button("📥 Add plan to calendar (.ics)", data=_ics,
                                   file_name=f"SkillBridge_{target_role.replace(' ', '_')}_plan.ics",
                                   mime="text/calendar", key="plan_ics")
            except Exception as e:
                st.caption(f"Calendar export unavailable: {e}")

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
                _hist_key = (ss.session or {}).get("user_id") or (ss.session or {}).get("username", "")
                if st.button("💾 Save my progress"):
                    ok = api_client.save_progress(ss.session, ss.auth_user, target_role,
                                                  projected["match_percent"], new_learned)
                    ss.learned = new_learned
                    cached_history.clear()     # new point saved -> drop stale cached reads
                    cached_export.clear()
                    if ok and api_client.is_api(ss.session):
                        st.success("Progress saved to your account (backend).")
                    elif ok:
                        st.success("Progress saved locally (backend offline).")
                    else:
                        st.warning("Couldn't save progress right now.")
                hist = cached_history(ss.session, _hist_key)
                if hist and len(hist) >= 2:
                    st.markdown('<div class="sec-label">📈 Your match score over time</div>',
                                unsafe_allow_html=True)
                    figh = go.Figure(go.Scatter(
                        x=list(range(1, len(hist) + 1)),
                        y=[h.get("score", 0) for h in hist],
                        mode="lines+markers", line_color="#3b82f6", marker=dict(size=8)))
                    figh.update_layout(height=240, margin=dict(t=10, b=10, l=10, r=10),
                                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                       font_color=CHART_FONT, yaxis_title="Match %",
                                       yaxis_range=[0, 100], xaxis_title="saved snapshots")
                    st.plotly_chart(_theme_fig(figh), width="stretch", theme=None, config=_PLOTLY_CFG)
                    st.caption(f"{len(hist)} saved snapshots — your readiness over time.")
                with st.expander("☁️ Your saved data (backend)"):
                    data = cached_export(ss.session, _hist_key)
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
            marker_color=["#ff7a36", "#3b82f6"], text=[f"{rA['match_percent']}%",
            f"{rB['match_percent']}%"], textposition="auto"))
        figc.update_layout(height=300, margin=dict(t=20, b=10, l=10, r=10),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font_color=CHART_FONT, yaxis_title="Match %", yaxis_range=[0, 100])
        st.plotly_chart(_theme_fig(figc), width="stretch", theme=None, config=_PLOTLY_CFG)

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
            # semantic: also catch skills THIS JD implies but doesn't name explicitly
            if semantic.index_exists():
                _jd_inf, _ = cached_semantic_skills(jd_text, tuple(jd_skills))
                if _jd_inf:
                    jd_skills = sorted(set(jd_skills) | set(_jd_inf))
                    _sset = set(student_skills)
                    _mt = [s for s in jd_skills if s in _sset]
                    jm = {"jd_skills": jd_skills, "matched": _mt,
                          "missing": [s for s in jd_skills if s not in _sset],
                          "match_percent": round(len(_mt) / len(jd_skills) * 100)}
                    note = "🧠 Included skills this job description implies (semantic match)."
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

    # ---- AI cover-letter generator (uses your skills + this JD) ----
    st.markdown("---")
    st.markdown('<div class="sec-label">✍️ AI cover letter</div>', unsafe_allow_html=True)
    if not student_skills:
        st.caption("Add your skills in the sidebar to generate a tailored cover letter.")
    else:
        _cl1, _cl2 = st.columns(2)
        _cl_company = _cl1.text_input("Company (optional)", key="cl_company")
        _cl_lang = _cl2.selectbox("Language", ["English", "Hindi", "Marathi"], key="cl_lang")
        if st.button("✍️ Generate cover letter", key="cl_btn"):
            _cl_prompt = cover_letter.build_cover_letter_prompt(
                ss.auth_user or "", target_role, student_skills,
                jd_text=jd_text, company=_cl_company, language=_cl_lang)
            with st.spinner("Writing your cover letter…"):
                _cl_text, _cl_err = gemini_generate(_cl_prompt)
            if _cl_err:
                show_ai_error(_cl_err)
            else:
                ss["cover_letter_text"] = _cl_text
        if ss.get("cover_letter_text"):
            st.markdown(ss["cover_letter_text"])
            st.download_button("⬇️ Download cover letter (.txt)", data=ss["cover_letter_text"],
                               file_name=f"CoverLetter_{target_role.replace(' ', '_')}.txt",
                               mime="text/plain", key="cl_dl")

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
            text, err = ai_market_pulse(target_role)
        if err:
            show_ai_error(err)
        else:
            ss.market_text = text
    if ss.market_text:
        st.markdown(ss.market_text)
    st.caption("Curated index is always-on; the AI pulse is an optional live read. "
               "We don't scrape job boards (ToS); this is the honest, deploy-safe version.")

# ---------------------------------------------------------------- SITE FOOTER
# Visible profile links (SEO audit: "create and link associated profiles").
st.markdown(
    '<div style="text-align:center; margin-top:26px; padding:12px 0 4px; '
    'color:var(--sub); font-size:.92rem;">'
    'Built by <strong>Darshan Dalvi</strong> &nbsp;·&nbsp; '
    f'<a href="{seo.GITHUB_URL}" target="_blank" rel="me noopener" '
    'style="color:var(--accent2); text-decoration:none;">GitHub</a> &nbsp;·&nbsp; '
    f'<a href="{seo.LINKEDIN_URL}" target="_blank" rel="me noopener" '
    'style="color:var(--accent2); text-decoration:none;">LinkedIn</a> &nbsp;·&nbsp; '
    f'<a href="{seo.REPO_URL}" target="_blank" rel="noopener" '
    'style="color:var(--accent2); text-decoration:none;">Source code</a>'
    '</div>', unsafe_allow_html=True)
