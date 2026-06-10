import streamlit as st
import requests
from datetime import datetime
from chatbot import (
    extract_video_id, get_transcript, create_vector_store,
    answer_question, generate_summary, generate_key_topics,
    generate_qa_pairs, generate_mcq_quiz,
)
from quiz_parser import parse_mcq, grade_quiz, export_txt
from utils import get_error_message

st.set_page_config(page_title="YouTube Intelligence", layout="wide", initial_sidebar_state="expanded")

# Inject premium ChatGPT Web CSS overrides
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background: #212121 !important; color: #FFFFFF !important;
    font-family: 'Inter', -apple-system, sans-serif !important; font-size: 13px !important;
}
[data-testid="stHeader"], footer, #MainMenu { display: none !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3A3A3A; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover { background: #4A4A4A; }

/* ── SIDEBAR STYLE ── */
[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #262626 !important;
    min-width: 280px !important; max-width: 280px !important; width: 280px !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarUserContent"],
[data-testid="stSidebarContent"] { 
    padding: 0 !important; 
    background: #111111 !important; 
}
[data-testid="stSidebarUserContent"] {
    padding: 24px 20px !important;
    background-color: #111111 !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}

/* Sidebar Headings */
.sb-group {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #71717A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-top: 20px !important;
    margin-bottom: 8px !important;
    padding-left: 2px !important;
}

/* Columns gap spacing & alignment */
[data-testid="stHorizontalBlock"] {
    gap: 12px !important;
    margin-bottom: 4px !important;
    align-items: center !important;
}

/* Sidebar secondary action buttons */
[data-testid="stSidebar"] div.stButton button {
    width: 100% !important;
    height: 36px !important;
    min-height: 36px !important;
    background-color: #171717 !important;
    border: 1px solid #262626 !important;
    color: #A1A1AA !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.15s ease !important;
    padding: 0 !important;
    margin-bottom: 8px !important;
}
[data-testid="stSidebar"] div.stButton button:hover {
    background-color: #2A2A2A !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}

/* Model Select Input Box */
[data-testid="stSidebar"] div[data-testid="stTextInput"] > div > div > input {
    background-color: #171717 !important;
    color: #FFFFFF !important;
    border: 1px solid #262626 !important;
    border-radius: 6px !important;
    padding: 6px 10px !important;
    font-size: 12.5px !important;
    height: 32px !important;
}

/* Hide the mdl input widget completely from view */
div[data-testid="stSidebar"] div[data-testid="stTextInput"]:has(input[id="mdl"]) {
    display: none !important;
}

/* Settings expander in sidebar */
[data-testid="stSidebar"] div[data-element-type="expandableContainer"] {
    background-color: transparent !important;
    border: 1px solid #262626 !important;
    border-radius: 6px !important;
    margin-bottom: 12px !important;
    margin-top: 8px !important;
}
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background-color: transparent !important;
    color: #A1A1AA !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
}
[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    color: #FFFFFF !important;
    background-color: #171717 !important;
}

/* Recent Session Compact Cards */
.sb-recent-card {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #171717;
    border: 1px solid #262626;
    border-radius: 6px;
    padding: 8px 12px;
    margin-bottom: 6px;
    transition: background-color 0.12s ease;
}
.sb-recent-card:hover {
    background-color: #2A2A2A;
}
.sb-recent-label {
    font-size: 12px;
    color: #A1A1AA;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
}

/* Status Info Section */
.sb-status-footer {
    margin-top: auto;
    padding-top: 16px;
    border-top: 1px solid #262626;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.sb-status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #A1A1AA;
    padding: 4px 0;
}
.sb-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}

/* ── MAIN AREA STYLE ── */
[data-testid="stMainBlockContainer"], .block-container {
    padding: 32px 40px 120px 40px !important; /* Increased bottom padding to prevent chat input overlap */
    max-width: 1000px !important;
    margin: 0 auto !important;
}

.page-hdr {
    text-align: center;
    padding-bottom: 24px;
    border-bottom: 1px solid #262626;
    margin-bottom: 32px;
}
.page-hdr-title {
    font-size: 36px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #A1A1AA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em !important;
    margin-bottom: 8px;
}
.page-hdr-sub {
    font-size: 14px !important;
    color: #8E8E93 !important;
    margin-top: 6px;
}

/* Premium KPI Cards */
.kpi-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.kpi-card {
    background: linear-gradient(135deg, #1e1e1e 0%, #141414 100%) !important;
    border: 1px solid #262626 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    position: relative;
    overflow: hidden;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}
.kpi-card:hover {
    transform: translateY(-2px) !important;
    border-color: #10A37F !important;
    box-shadow: 0 8px 30px rgba(16, 163, 127, 0.15) !important;
}
.kpi-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.kpi-icon-wrapper {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.25s;
}
.kpi-card:hover .kpi-icon-wrapper {
    background: rgba(16, 163, 127, 0.1);
}
.kpi-label {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #71717A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.kpi-value {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    margin-top: 4px;
    line-height: 1.2;
}
.kpi-sub {
    font-size: 11.5px !important;
    color: #A1A1AA !important;
    margin-top: 2px;
}

.row-label {
    font-size: 12px;
    font-weight: 600;
    color: #8E8E93;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

/* Video Source card using :has selector */
div[data-testid="stHorizontalBlock"]:has(div.st-key-vurl) {
    background: #171717 !important;
    border: 1px solid #262626 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin-bottom: 32px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
}

/* Video Source text input style */
div.st-key-vurl div[data-testid="stTextInput"] input {
    background-color: #2F2F2F !important;
    color: #FFFFFF !important;
    border: 1px solid #3A3A3A !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 13.5px !important;
    font-family: 'Inter', sans-serif !important;
    height: 40px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
div.st-key-vurl div[data-testid="stTextInput"] input:focus {
    border-color: #10A37F !important;
    box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2) !important;
}

/* Zero out margins to ensure perfect vertical alignment */
div.st-key-vurl div[data-testid="stTextInput"],
div.st-key-lbtn div.stButton {
    margin-bottom: 0px !important;
    padding-bottom: 0px !important;
}

/* Primary buttons (ChatGPT Green) & Form submit buttons */
button[data-testid*="primary"],
div.stFormSubmitButton button {
    background-color: #10A37F !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    height: 40px !important;
    transition: background-color 0.15s ease, box-shadow 0.15s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}
button[data-testid*="primary"]:hover,
div.stFormSubmitButton button:hover {
    background-color: #0d8769 !important;
    box-shadow: 0 2px 10px rgba(16, 163, 127, 0.25) !important;
}

/* Specific overrides for sidebar New Analysis button */
div.st-key-new_analysis button {
    width: 160px !important;
    height: 38px !important;
    min-width: 160px !important;
    max-width: 160px !important;
    min-height: 38px !important;
    border-radius: 19px !important; /* Pill shape */
    background-color: #10A37F !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    margin: 16px auto !important; /* Centered with spacing */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div.st-key-new_analysis button:hover {
    background-color: #0d8769 !important;
}

/* Load button inside Video Source block */
div.st-key-lbtn button {
    width: 100% !important;
    height: 40px !important;
}

/* Alert boxes */
.alert {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.5;
    margin-bottom: 20px;
}
.alert-err  { background: rgba(239, 68, 68, 0.07); border: 1px solid rgba(239, 68, 68, 0.2); color: #FCA5A5; }
.alert-ok   { background: rgba(16, 185, 129, 0.07); border: 1px solid rgba(16, 185, 129, 0.2); color: #6EE7B7; }
.alert-info { background: rgba(37, 99, 235, 0.07); border: 1px solid rgba(37, 99, 235, 0.2); color: #93C5FD; }

.sec-hd {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #71717A !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin: 24px 0 12px !important;
}

/* Conversational Bubble Chat layout */
.chat-wrap {
    display: flex;
    flex-direction: column;
    gap: 16px;
    max-width: 860px;
    margin: 0 auto;
}
.cmsg {
    display: flex;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 1px solid #262626;
    animation: fin 0.18s ease-out;
}
@keyframes fin { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.cmsg-user {
    flex-direction: row-reverse;
}
.cavatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 10px;
    font-weight: 700;
}
.cav-u { background: #4F46E5; color: #FFFFFF; }
.cav-a { background: #10A37F; color: #FFFFFF; }
.cbody { flex: 1; min-width: 0; }
.crole { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #71717A; margin-bottom: 3px; }
.ctext { font-size: 14px; line-height: 1.65; color: #FFFFFF; white-space: pre-wrap; word-break: break-word; }
.cmsg-user .cbody { display: flex; flex-direction: column; align-items: flex-end; }
.cmsg-user .ctext {
    background: #2F2F2F;
    border: 1px solid #3A3A3A;
    border-radius: 20px;
    padding: 10px 18px;
    color: #FFFFFF;
    max-width: 75%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}
.cmsg-user .crole { text-align: right; }

/* Premium result card for Summary/Key Points/Topics etc. */
.res-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 12px;
    padding: 20px;
    font-size: 14px;
    color: #FFFFFF;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* Chat GPT Bottom Sticky Input Field overrides */
.stChatInputContainer {
    position: fixed !important;
    left: 280px !important;
    right: 0 !important;
    max-width: 860px !important;
    margin: 0 auto !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 16px 16px 16px !important;
    bottom: 0px !important;
    z-index: 999999 !important;
}
div[data-testid="stChatInput"] {
    background-color: #2F2F2F !important;
    border: 1px solid #3A3A3A !important;
    border-radius: 24px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    width: 100% !important;
    overflow: hidden !important;
}
div[data-testid="stChatInput"] textarea {
    color: #FFFFFF !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    background-color: transparent !important;
    border: none !important;
    padding: 12px 52px 12px 16px !important;
}
div[data-testid="stChatInput"] button {
    position: absolute !important;
    background-color: #10A37F !important;
    color: #FFFFFF !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    right: 8px !important;
    bottom: 8px !important;
    transition: background-color 0.15s ease !important;
}
div[data-testid="stChatInput"] button:hover {
    background-color: #0d8769 !important;
}
div[data-testid="stChatInput"] button svg {
    width: 16px !important;
    height: 16px !important;
}

/* Q&A Cards */
.qa-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 14px;
    transition: border-color 0.2s ease;
}
.qa-card:hover {
    border-color: #10A37F;
}
.qa-q {
    font-size: 14px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
}
.qa-a {
    font-size: 13.5px;
    color: #D1D1D6;
    line-height: 1.6;
}

/* Back to chat buttons */
div.st-key-qa_back button,
div.st-key-quiz_back button {
    background-color: #171717 !important;
    border: 1px solid #262626 !important;
    color: #A1A1AA !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    height: 40px !important;
    transition: all 0.15s ease !important;
}
div.st-key-qa_back button:hover,
div.st-key-quiz_back button:hover {
    background-color: #2A2A2A !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}

/* Quiz questions and custom interactive radio selections */
.quiz-q-card {
    background: #171717;
    border: 1px solid #262626;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.quiz-q-num {
    font-size: 11px;
    font-weight: 700;
    color: #10A37F;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}
.quiz-q-text {
    font-size: 14px;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1.5;
}

/* Style radio group options as interactive list items */
div[role="radiogroup"] label {
    background: #171717 !important;
    border: 1px solid #262626 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    transition: all 0.18s ease !important;
}
div[role="radiogroup"] label:hover {
    background: #222222 !important;
    border-color: #3A3A3A !important;
}
div[role="radiogroup"] label:has(input:checked) {
    border-color: #10A37F !important;
    background: rgba(16, 163, 127, 0.04) !important;
}
div[role="radiogroup"] label input:checked + div {
    border-color: #10A37F !important;
    background-color: #10A37F !important;
}
/* Style the dot inside checked radio to be ChatGPT Green */
div[role="radiogroup"] label input:checked + div div {
    background-color: #10A37F !important;
}
div[role="radiogroup"] label:has(input:checked) div[data-checked="true"] {
    background-color: #10A37F !important;
    border-color: #10A37F !important;
}
div[role="radiogroup"] label div[data-checked="true"] div {
    background-color: #10A37F !important;
}

/* Score banner & cells styling */
.score-banner { background:#171717; border:1px solid #262626; border-radius:12px; padding:20px 24px; margin-bottom:20px; }
.score-main { font-size:36px; font-weight:800; color:#FFFFFF; letter-spacing:-0.03em; }
.score-pct { font-size:15px; color:#A1A1AA; margin-top:2px; }
.score-grade { font-size:32px; font-weight:800; letter-spacing:-0.02em; }
.score-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:16px; }
.score-cell { background:#111111; border:1px solid #262626; border-radius:8px; padding:12px; text-align:center; }
.score-cell-val { font-size:22px; font-weight:700; color:#FFFFFF; }
.score-cell-lbl { font-size:10px; color:#71717A; text-transform:uppercase; letter-spacing:0.06em; margin-top:4px; }

/* Download & Retake Buttons styling */
div.stDownloadButton button {
    background-color: #10A37F !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    height: 40px !important;
    transition: background-color 0.15s ease, box-shadow 0.15s ease !important;
}
div.stDownloadButton button:hover {
    background-color: #0d8769 !important;
    box-shadow: 0 2px 10px rgba(16, 163, 127, 0.25) !important;
}
div.st-key-retake button {
    background-color: #171717 !important;
    border: 1px solid #262626 !important;
    color: #A1A1AA !important;
    border-radius: 8px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    height: 40px !important;
    transition: all 0.15s ease !important;
}
div.st-key-retake button:hover {
    background-color: #2A2A2A !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}

/* Quiz Review Items styling */
.rev-item { border-radius:8px; padding:14px 16px; margin-bottom:8px; border:1px solid; }
.rev-correct { background:rgba(16,185,129,0.04); border-color:rgba(16,185,129,0.15); }
.rev-wrong   { background:rgba(239,68,68,0.04); border-color:rgba(239,68,68,0.15); }
.rev-qtext { font-size:13.5px; font-weight:600; color:#FFFFFF; margin-bottom:8px; }
.rev-row { display:flex; gap:10px; font-size:12.5px; margin-top:4px; }
.rev-label { color:#71717A; font-weight:500; min-width:110px; }
.rev-val-ok  { color:#10B981; font-weight:600; }
.rev-val-err { color:#EF4444; font-weight:600; }
.rev-val-neu { color:#A1A1AA; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ── ICON HELPER ────────────────────────────────────────────────────────────────
def si(d: str, s: int = 13, c: str = "#71717A") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 24 24" '
            f'fill="none" stroke="{c}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">{d}</svg>')

IC = {
    "video":  '<polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2"/>',
    "clock":  '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "act":    '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "cpu":    '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    "zap":    '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "link":   '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "send":   '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
    "check":  '<polyline points="20 6 9 17 4 12"/>',
    "alert":  '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "bot":    '<rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8.01" y2="16"/><line x1="16" y1="16" x2="16.01" y2="16"/>',
    "doc":    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
    "msg":    '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "qa":     '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "quiz":   '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
    "dl":     '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M10 14.66V17c0 .55-.45 1-1 1H4v2h16v-2h-5c-.55 0-1-.45-1-1v-2.34M12 2a7 7 0 0 0-7 7c0 2.45 1.25 4.6 3.14 5.86h7.72A7.53 7.53 0 0 0 19 9a7 7 0 0 0-7-7z"/>',
    "hash":   '<line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/><line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>',
}


# ── SESSION STATE ──────────────────────────────────────────────────────────────
def init_state():
    for k, v in {
        "vector_store": None, "transcript": "", "num_chunks": 0,
        "video_id": None, "last_output": "", "last_error": "",
        "chat_history": [], "session_history": [],
        "questions_asked": 0, "transcript_loaded": False,
        "qa_pairs_raw": "",
        "quiz_questions": [], "quiz_answers": {}, "quiz_result": None,
        "quiz_submitted": False, "quiz_history": [],
        "active_panel": "chat",
        "mdl": "llama3",
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

model_name = st.session_state.get("mdl", "llama3")


# ── BACKEND WRAPPERS ───────────────────────────────────────────────────────────
def check_ollama(model: str):
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        models = [m["name"] for m in r.json().get("models", [])]
        return True, models
    except Exception:
        return False, []


def do_load(url: str, model: str):
    st.session_state.last_error = ""
    st.session_state.last_output = ""
    try:
        vid = extract_video_id(url)
    except ValueError as e:
        st.session_state.last_error = str(e)
        return False, str(e), None

    print(f"[DEBUG] URL={url}  ID={vid}")
    st.session_state.video_id = vid
    try:
        transcript = get_transcript(vid)
        vs, nc = create_vector_store(transcript)
        st.session_state.transcript = transcript
        st.session_state.vector_store = vs
        st.session_state.num_chunks = nc
        st.session_state.transcript_loaded = True
        st.session_state.chat_history = []
        st.session_state.quiz_questions = []
        st.session_state.quiz_result = None
        st.session_state.quiz_submitted = False
        st.session_state.quiz_answers = {}
        st.session_state.qa_pairs_raw = ""
        st.session_state.session_history = (
            [{"vid": vid, "ts": datetime.now().strftime("%H:%M")}]
            + st.session_state.session_history
        )[:10]
        return True, f"{nc} chunks indexed", vid
    except Exception as e:
        st.session_state.transcript_loaded = False
        st.session_state.last_error = str(e)
        return False, str(e), vid


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # 1. Header (Centered, compact, no logo)
    st.markdown("""
    <div class="sb-header">
        <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em;">YouTube Intelligence</div>
        <div style="font-size: 12px; color: #A1A1AA; margin-top: 4px;">AI Video Analysis</div>
    </div>""", unsafe_allow_html=True)

    # 2. New Analysis (Centered, single button, 160px x 38px)
    if st.button("+ New Analysis", key="new_analysis", type="primary"):
        for k, default in [
            ("vector_store", None), ("transcript", ""), ("num_chunks", 0),
            ("video_id", None), ("last_output", ""), ("last_error", ""),
            ("chat_history", []), ("quiz_questions", []), ("quiz_answers", {}),
            ("quiz_result", None), ("quiz_submitted", False),
            ("qa_pairs_raw", ""), ("transcript_loaded", False),
        ]:
            st.session_state[k] = default
        st.session_state.active_panel = "chat"
        st.rerun()

    ollama_ok, available_models = check_ollama(model_name)
    model_found = ollama_ok and any(model_name in m for m in available_models)
    tr_loaded = st.session_state.transcript_loaded
    active = st.session_state.active_panel

    # 3. Settings Folders (Tucks away model select to prevent header overlaps)
    with st.expander("Settings", expanded=False):
        model_name = st.text_input("Ollama Model", key="mdl", label_visibility="collapsed")

    # 4. Recent Sessions (Compact cards, no timestamps, fallback to specified names)
    st.markdown('<div class="sb-group">Recent Sessions</div>', unsafe_allow_html=True)
    
    sessions_to_show = []
    if st.session_state.session_history:
        for it in st.session_state.session_history[:5]:
            label = it.get("title") or it["vid"]
            sessions_to_show.append(label)
    else:
        sessions_to_show = ["Agentic AI Lecture", "LangChain Tutorial", "Python Basics"]
        
    for label in sessions_to_show:
        st.markdown(f"""
        <div class="sb-recent-card">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#A1A1AA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span class="sb-recent-label">{label}</span>
        </div>""", unsafe_allow_html=True)

    # 5. AI Tools
    st.markdown('<div class="sb-group">AI Tools</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Summary", key="t_sum"):
            if not st.session_state.vector_store:
                st.session_state.last_error = "Load a video first."
            else:
                with st.spinner("Summary..."):
                    try:
                        res = generate_summary(st.session_state.vector_store, model_name)
                        st.session_state.last_output = res
                        st.session_state.active_panel = "chat"
                        st.session_state.last_error = ""
                    except Exception as e:
                        st.session_state.last_error = str(e)
    with col2:
        if st.button("Key Points", key="t_kp"):
            if not st.session_state.vector_store:
                st.session_state.last_error = "Load a video first."
            else:
                with st.spinner("Key Points..."):
                    try:
                        res = generate_key_topics(st.session_state.vector_store, model_name)
                        st.session_state.last_output = res
                        st.session_state.active_panel = "chat"
                        st.session_state.last_error = ""
                    except Exception as e:
                        st.session_state.last_error = str(e)
                        
    col3, col4 = st.columns(2)
    with col3:
        if st.button("Topics", key="t_top"):
            if not st.session_state.vector_store:
                st.session_state.last_error = "Load a video first."
            else:
                with st.spinner("Topics..."):
                    try:
                        res = generate_key_topics(st.session_state.vector_store, model_name)
                        st.session_state.last_output = res
                        st.session_state.active_panel = "chat"
                        st.session_state.last_error = ""
                    except Exception as e:
                        st.session_state.last_error = str(e)

    # 6. Learning
    st.markdown('<div class="sb-group">Learning</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Q&A", key="t_qa"):
            if not st.session_state.vector_store:
                st.session_state.last_error = "Load a video first."
            else:
                with st.spinner("Generating Q&A..."):
                    try:
                        st.session_state.qa_pairs_raw = generate_qa_pairs(st.session_state.vector_store, model_name)
                        st.session_state.active_panel = "qa"
                        st.session_state.last_error = ""
                    except Exception as e:
                        st.session_state.last_error = str(e)
                st.rerun()
    with col2:
        if st.button("Quiz", key="t_quiz"):
            if not st.session_state.vector_store:
                st.session_state.last_error = "Load a video first."
            else:
                with st.spinner("Generating quiz..."):
                    try:
                        raw = generate_mcq_quiz(st.session_state.vector_store, model_name, num_questions=7)
                        questions = parse_mcq(raw)
                        if not questions:
                            st.session_state.last_error = "Could not parse quiz. Try again."
                        else:
                            st.session_state.quiz_questions = questions
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_result = None
                            st.session_state.quiz_submitted = False
                            st.session_state.active_panel = "quiz"
                            st.session_state.last_error = ""
                    except Exception as e:
                        st.session_state.last_error = str(e)
                st.rerun()

    # 7. Content
    st.markdown('<div class="sb-group">Content</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Transcript", key="t_tr"):
            if not st.session_state.transcript:
                st.session_state.last_error = "Load a video first."
            else:
                st.session_state.last_output = st.session_state.transcript[:3000]
                st.session_state.active_panel = "chat"
                st.session_state.last_error = ""
    with col2:
        if st.button("Export", key="t_export"):
            st.session_state.last_error = "PDF export: use Download TXT from quiz results."

    # 8. Status footer (Compact style moved to bottom)
    ollama_color = "#10B981" if ollama_ok else "#EF4444"
    model_color = "#10B981" if model_found else ("#F59E0B" if ollama_ok else "#EF4444")
    tr_color = "#10B981" if tr_loaded else "#3F3F46"
    
    st.markdown(f"""
    <div class="sb-status-footer">
        <div class="sb-status-item"><span class="sb-status-dot" style="background-color: {ollama_color};"></span>Ollama {'Online' if ollama_ok else 'Offline'}</div>
        <div class="sb-status-item"><span class="sb-status-dot" style="background-color: {tr_color};"></span>Transcript {'Loaded' if tr_loaded else 'Not Loaded'}</div>
        <div class="sb-status-item"><span class="sb-status-dot" style="background-color: {model_color};"></span>{model_name}</div>
    </div>""", unsafe_allow_html=True)


# ── MAIN WORKSPACE ────────────────────────────────────────────────────────────
st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

# Main Title Block
st.markdown("""
<div class="page-hdr">
    <div class="page-hdr-title">YouTube Intelligence</div>
    <div class="page-hdr-sub">Analyze and chat with YouTube videos using local AI</div>
</div>
""", unsafe_allow_html=True)

# KPI dashboard
words = len(st.session_state.transcript.split()) if st.session_state.transcript else 0
best_score = f"{st.session_state.quiz_history[-1]['percentage']}%" if st.session_state.quiz_history else "—"
st.markdown(f"""
<div class="kpi-bar">
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-label">Transcript</span>
            <span class="kpi-icon-wrapper">{si(IC["doc"], 14, "#10A37F")}</span>
        </div>
        <div class="kpi-value">{len(st.session_state.transcript):,}</div>
        <div class="kpi-sub">{words:,} words</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-label">Chunks</span>
            <span class="kpi-icon-wrapper">{si(IC["layers"], 14, "#10A37F")}</span>
        </div>
        <div class="kpi-value">{st.session_state.num_chunks}</div>
        <div class="kpi-sub">FAISS indexed</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-label">Questions</span>
            <span class="kpi-icon-wrapper">{si(IC["msg"], 14, "#10A37F")}</span>
        </div>
        <div class="kpi-value">{st.session_state.questions_asked}</div>
        <div class="kpi-sub">asked this session</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-card-header">
            <span class="kpi-label">Last Quiz</span>
            <span class="kpi-icon-wrapper">{si(IC["trophy"], 14, "#10A37F")}</span>
        </div>
        <div class="kpi-value">{best_score}</div>
        <div class="kpi-sub">{'grade ' + st.session_state.quiz_history[-1]['grade'] if st.session_state.quiz_history else 'no quiz yet'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Video URL Row (Width 75% input, remaining load button of 90px x 40px)
st.markdown(f'<div class="row-label">Video Source</div>', unsafe_allow_html=True)
col1, col2 = st.columns([7, 1], gap="small")
with col1:
    video_url = st.text_input("u", placeholder="Enter YouTube URL or Video ID...", label_visibility="collapsed", key="vurl")
with col2:
    load_btn = st.button("Load", type="primary", key="lbtn", use_container_width=True)

if load_btn:
    if not video_url or not video_url.strip():
        st.markdown(f'<div class="alert alert-err">{si(IC["alert"],13,"#FCA5A5")} {get_error_message("empty_url")}</div>',
                    unsafe_allow_html=True)
    else:
        with st.spinner("Fetching transcript..."):
            ok, msg, vid = do_load(video_url.strip(), model_name)
        if ok:
            st.markdown(f'<div class="alert alert-ok">{si(IC["check"],13,"#6EE7B7")} {msg} — <code style="font-size:11px;">{vid}</code></div>',
                        unsafe_allow_html=True)
            st.rerun()
        else:
            st.markdown(f'<div class="alert alert-err">{si(IC["alert"],13,"#FCA5A5")} Transcript failed — <code style="font-size:11px;">{vid}</code></div>',
                        unsafe_allow_html=True)
            st.code(msg)

if st.session_state.last_error and not load_btn:
    st.markdown(f'<div class="alert alert-err">{si(IC["alert"],13,"#FCA5A5")} {st.session_state.last_error}</div>',
                unsafe_allow_html=True)


# ── PANEL: CHAT ────────────────────────────────────────────────────────────────
if st.session_state.active_panel == "chat":

    if st.session_state.last_output:
        st.markdown(f'<div class="sec-hd">Result</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="res-card">{st.session_state.last_output}</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        st.markdown(f'<div class="sec-hd">Conversation</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"""
                <div class="cmsg cmsg-user">
                    <div class="cavatar cav-u">You</div>
                    <div class="cbody"><div class="crole">You</div><div class="ctext">{m["text"]}</div></div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cmsg">
                    <div class="cavatar cav-a">{si(IC["bot"],12,"#71717A")}</div>
                    <div class="cbody"><div class="crole">AI</div><div class="ctext">{m["text"]}</div></div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ChatGPT style bottom sticky input bar
    question = st.chat_input("Ask anything about this video...")
    if question:
        if not st.session_state.vector_store:
            st.markdown(f'<div class="alert alert-info">{si(IC["alert"],13,"#93C5FD")} Load a video first.</div>',
                        unsafe_allow_html=True)
        else:
            st.session_state.chat_history.append({"role": "user", "text": question})
            st.session_state.questions_asked += 1
            with st.spinner("Thinking..."):
                try:
                    ans = answer_question(question, st.session_state.vector_store, model_name)
                    st.session_state.chat_history.append({"role": "assistant", "text": ans})
                    st.session_state.last_error = ""
                except RuntimeError as e:
                    err = get_error_message("ollama_not_running") if "Ollama" in str(e) else str(e)
                    st.session_state.chat_history.append({"role": "assistant", "text": f"Error: {err}"})
                    st.session_state.last_error = err
                except Exception as e:
                    st.session_state.chat_history.append({"role": "assistant", "text": f"Error: {e}"})
                    st.session_state.last_error = str(e)
            st.rerun()


# ── PANEL: Q&A ─────────────────────────────────────────────────────────────────
elif st.session_state.active_panel == "qa":

    hdr_col, back_col = st.columns([5, 1], gap="small")
    with hdr_col:
        st.markdown(f'<div class="sec-hd" style="margin-top:4px;">Q&amp;A — Questions &amp; Answers</div>',
                    unsafe_allow_html=True)
    with back_col:
        if st.button("Back to Chat", key="qa_back", use_container_width=True):
            st.session_state.active_panel = "chat"
            st.rerun()

    raw = st.session_state.qa_pairs_raw
    if not raw:
        st.markdown('<div class="alert alert-info">No Q&A generated yet. Click Q&A in the sidebar.</div>',
                    unsafe_allow_html=True)
    else:
        pairs, current_q, current_a = [], "", ""
        for line in raw.splitlines():
            line = line.strip()
            if line.lower().startswith("q:"):
                if current_q:
                    pairs.append((current_q, current_a.strip()))
                current_q = line[2:].strip()
                current_a = ""
            elif line.lower().startswith("a:"):
                current_a = line[2:].strip()
            elif current_a:
                current_a += " " + line
        if current_q:
            pairs.append((current_q, current_a.strip()))

        if not pairs:
            st.markdown(f'<div class="res-card">{raw}</div>', unsafe_allow_html=True)
        else:
            for i, (q, a) in enumerate(pairs, 1):
                st.markdown(f"""
                <div class="qa-card">
                    <div class="qa-q">Q{i}. {q}</div>
                    <div class="qa-a">{a}</div>
                </div>""", unsafe_allow_html=True)


# ── PANEL: QUIZ ────────────────────────────────────────────────────────────────
elif st.session_state.active_panel == "quiz":

    questions = st.session_state.quiz_questions
    hdr_col, back_col = st.columns([5, 1], gap="small")
    with hdr_col:
        st.markdown(f'<div class="sec-hd" style="margin-top:4px;">Interactive Quiz — {len(questions)} Questions</div>',
                    unsafe_allow_html=True)
    with back_col:
        if st.button("Back to Chat", key="quiz_back", use_container_width=True):
            st.session_state.active_panel = "chat"
            st.rerun()

    if not questions:
        st.markdown('<div class="alert alert-info">No quiz loaded. Click Quiz in the sidebar.</div>',
                    unsafe_allow_html=True)

    elif not st.session_state.quiz_submitted:
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                opts = q["options"]
                st.markdown(f"""
                <div class="quiz-q-card">
                    <div class="quiz-q-num">Question {i+1} of {len(questions)}</div>
                    <div class="quiz-q-text">{q['question']}</div>
                </div>""", unsafe_allow_html=True)
                chosen = st.radio(
                    f"q_{i}", options=list(sorted(opts.keys())),
                    format_func=lambda k, o=opts: f"{k}.  {o[k]}",
                    key=f"radio_{i}", label_visibility="collapsed",
                    index=None,
                )
                st.session_state.quiz_answers[i] = chosen or ""
                st.markdown("<hr style='border-color:#262626;margin:8px 0;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Submit Quiz", type="primary", use_container_width=True)

        if submitted:
            incomplete = [idx for idx, ans in st.session_state.quiz_answers.items() if not ans]
            if incomplete:
                st.error("Please answer all questions before submitting the quiz!")
            else:
                result = grade_quiz(questions, st.session_state.quiz_answers)
                st.session_state.quiz_result = result
                st.session_state.quiz_submitted = True
                st.session_state.quiz_history.append(result)
                st.rerun()

    else:
        result = st.session_state.quiz_result
        grade_color = {"A+": "#10B981", "A": "#10B981", "B": "#3B82F6",
                       "C": "#F59E0B", "D": "#F97316", "F": "#EF4444"}.get(result["grade"], "#A1A1AA")

        st.markdown(f"""
        <div class="score-banner">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <div>
                    <div class="score-main">{result['correct']}/{result['total']}</div>
                    <div class="score-pct">{result['percentage']}% &nbsp;&middot;&nbsp; {result['total']} questions</div>
                </div>
                <div class="score-grade" style="color:{grade_color};">{result['grade']}</div>
            </div>
            <div class="score-grid">
                <div class="score-cell"><div class="score-cell-val">{result['total']}</div><div class="score-cell-lbl">Total</div></div>
                <div class="score-cell"><div class="score-cell-val" style="color:#10B981;">{result['correct']}</div><div class="score-cell-lbl">Correct</div></div>
                <div class="score-cell"><div class="score-cell-val" style="color:#EF4444;">{result['wrong']}</div><div class="score-cell-lbl">Wrong</div></div>
                <div class="score-cell"><div class="score-cell-val" style="color:{grade_color};">{result['percentage']}%</div><div class="score-cell-lbl">Score</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        dl_col, rt_col, _ = st.columns([1, 1, 3], gap="small")
        with dl_col:
            st.download_button(
                label="Download TXT",
                data=export_txt(result, st.session_state.video_id or "unknown"),
                file_name=f"quiz_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain", use_container_width=True,
            )
        with rt_col:
            if st.button("Retake Quiz", key="retake", use_container_width=True):
                st.session_state.quiz_answers = {}
                st.session_state.quiz_result = None
                st.session_state.quiz_submitted = False
                st.rerun()

        st.markdown(f'<div class="sec-hd" style="margin-top:18px;">Review</div>',
                    unsafe_allow_html=True)
        for r in result["review"]:
            css = "rev-correct" if r["is_correct"] else "rev-wrong"
            ua_css = "rev-val-ok" if r["is_correct"] else "rev-val-err"
            indicator = si(IC["check"], 13, "#10B981") if r["is_correct"] else si(IC["alert"], 13, "#EF4444")
            st.markdown(f"""
            <div class="rev-item {css}">
                <div style="display:flex;align-items:flex-start;gap:8px;">
                    <div style="margin-top:1px;flex-shrink:0;">{indicator}</div>
                    <div style="flex:1;">
                        <div class="rev-qtext">Q{r['num']}. {r['question']}</div>
                        <div class="rev-row"><span class="rev-label">Your answer</span><span class="{ua_css}">{r['user_answer']}. {r['user_text']}</span></div>
                        <div class="rev-row"><span class="rev-label">Correct answer</span><span class="rev-val-ok">{r['correct_answer']}. {r['correct_text']}</span></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        if len(st.session_state.quiz_history) > 1:
            st.markdown(f'<div class="sec-hd" style="margin-top:18px;">Quiz History</div>',
                        unsafe_allow_html=True)
            for i, hr in enumerate(reversed(st.session_state.quiz_history), 1):
                gc = {"A+": "#10B981", "A": "#10B981", "B": "#3B82F6",
                      "C": "#F59E0B", "D": "#F97316", "F": "#EF4444"}.get(hr["grade"], "#A1A1AA")
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:7px 12px;background:#111111;border:1px solid #262626;border-radius:6px;margin-bottom:5px;">
                    <span style="font-size:12px;color:#A1A1AA;">Attempt {len(st.session_state.quiz_history)+1-i}</span>
                    <span style="font-size:12px;color:#FFFFFF;font-weight:600;">{hr['correct']}/{hr['total']}</span>
                    <span style="font-size:12px;color:#A1A1AA;">{hr['percentage']}%</span>
                    <span style="font-size:13px;font-weight:700;color:{gc};">{hr['grade']}</span>
                </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
