import streamlit as st
import requests
from chatbot import (
    extract_video_id,
    get_transcript,
    create_vector_store,
    answer_question,
    generate_summary,
    generate_key_topics,
    generate_quiz,
)
from utils import get_error_message

st.set_page_config(page_title="TubeQA AI — Video Intelligence Assistant", layout="wide")

# Inject premium CSS design system
st.markdown(
    """
    <style>
    /* BASE LAYOUT */
    [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        color: #F8FAFC !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.03) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.03) 0px, transparent 50%) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(3, 7, 18, 0.55) !important;
        backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 1.5rem !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }

    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        backdrop-filter: blur(8px) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 20px !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(59, 130, 246, 0.2) !important;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.05) !important;
    }

    /* BADGES & PILLS */
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    .status-online {
        background: rgba(16, 185, 129, 0.06) !important;
        border: 1px solid rgba(16, 185, 129, 0.15) !important;
        color: #10B981 !important;
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.06) !important;
        border: 1px solid rgba(239, 68, 68, 0.15) !important;
        color: #EF4444 !important;
    }
    .status-warning {
        background: rgba(245, 158, 11, 0.06) !important;
        border: 1px solid rgba(245, 158, 11, 0.15) !important;
        color: #F59E0B !important;
    }
    .status-dot {
        height: 6px;
        width: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.5rem;
        padding-left: 4px;
    }
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #F8FAFC 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* INPUTS & TEXT AREAS */
    div[data-testid="stTextInput"] > div > div > input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    div[data-testid="stWidgetLabel"] p {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        margin-bottom: 6px !important;
    }

    /* BUTTONS */
    button[data-testid="baseButton-secondary"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 38px !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background-color: rgba(59, 130, 246, 0.08) !important;
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.12) !important;
        transform: translateY(-1px) !important;
    }
    button[data-testid="baseButton-secondary"]:active {
        transform: translateY(1px) !important;
    }

    /* CODE BLOCKS */
    div[data-testid="stCodeBlock"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stCodeBlock"] pre {
        background-color: transparent !important;
        color: #E2E8F0 !important;
    }

    /* CHAT FEED */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .chat-bubble {
        padding: 14px 18px;
        border-radius: 12px;
        max-width: 85%;
        line-height: 1.6;
        font-size: 0.95rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        animation: fadeIn 0.3s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-bubble-user {
        background: rgba(59, 130, 246, 0.08) !important;
        border: 1px solid rgba(59, 130, 246, 0.15) !important;
        color: #F8FAFC !important;
        align-self: flex-end;
        border-bottom-right-radius: 2px;
    }
    .chat-bubble-assistant {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #F8FAFC !important;
        align-self: flex-start;
        border-bottom-left-radius: 2px;
    }
    .chat-header {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* STREAMLIT BRANDS */
    [data-testid="stToolbar"] {
        right: 20px !important;
    }
    footer {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    for key, val in [
        ("vector_store", None),
        ("transcript", ""),
        ("num_chunks", 0),
        ("video_id", None),
        ("last_output", ""),
        ("last_error", ""),
        ("history", []),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val


init_state()


# Sidebar Section Header Helper (Emoji-free, premium SVGs)
def sidebar_section_header(title: str, svg_inner: str):
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 24px; margin-bottom: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.8;">{svg_inner}</svg>
            <span style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94A3B8;">{title}</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# ── Startup diagnostics ──────────────────────────────────────────────────────
def check_ollama(model_name: str):
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code != 200:
            return False, "Ollama running but returned unexpected status.", []
        models = [m["name"] for m in r.json().get("models", [])]
        return True, "Ollama is running.", models
    except Exception as e:
        return False, f"Ollama not reachable: {e}", []


# ── Video loader ─────────────────────────────────────────────────────────────
def load_video(url: str, model_name: str):
    st.session_state.last_error = ""
    st.session_state.last_output = ""

    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span style="color: #EF4444; font-weight: 500; font-size: 0.95rem;">{get_error_message('invalid_url')} — {e}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    print(f"[DEBUG] Original URL   : {url}")
    print(f"[DEBUG] Extracted ID   : {video_id}")
    st.session_state.video_id = video_id

    with st.spinner("Fetching transcript and building index…"):
        try:
            transcript = get_transcript(video_id)
            vector_store, num_chunks = create_vector_store(transcript)
            st.session_state.transcript = transcript
            st.session_state.vector_store = vector_store
            st.session_state.num_chunks = num_chunks
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    <span style="color: #10B981; font-weight: 500; font-size: 0.95rem;">Video loaded — {num_chunks} chunks indexed.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        except RuntimeError as e:
            msg = str(e)
            st.markdown(
                """
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span style="color: #EF4444; font-weight: 500; font-size: 0.95rem;">Transcript retrieval failed.</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.9rem; color: #94A3B8;">
                    Video ID: <code style="color: #F8FAFC; background: rgba(0,0,0,0.25); padding: 2px 6px; border-radius: 4px;">{video_id}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.code(msg)
            st.session_state.last_error = msg
        except Exception as e:
            msg = str(e)
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span style="color: #EF4444; font-weight: 500; font-size: 0.95rem;">Unexpected error: {msg}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.9rem; color: #94A3B8;">
                    Video ID: <code style="color: #F8FAFC; background: rgba(0,0,0,0.25); padding: 2px 6px; border-radius: 4px;">{video_id}</code>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.session_state.last_error = msg


# ── Layout ───────────────────────────────────────────────────────────────────
# Header UI
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 1rem;">
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%); padding: 10px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#F8FAFC" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
        </div>
        <div>
            <h1 style="font-size: 1.75rem; font-weight: 800; letter-spacing: -0.03em; margin: 0; background: linear-gradient(135deg, #F8FAFC 30%, #94A3B8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">TubeQA AI</h1>
            <p style="font-size: 0.875rem; color: #94A3B8; margin: 2px 0 0 0;">Premium Video Intelligence & Chat Assistant</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    # Title & Logo
    st.markdown(
        """
        <div class="sidebar-logo">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
            <span class="sidebar-title">TubeQA AI</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    sidebar_section_header("Engine Config", '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>')
    model_name = st.text_input("Ollama Model", value="llama3")

    # Diagnostics
    ollama_ok, ollama_msg, available_models = check_ollama(model_name)
    if ollama_ok:
        st.markdown(
            f"""
            <div class="status-badge status-online">
                <span class="status-dot" style="background-color: #10B981; box-shadow: 0 0 8px #10B981;"></span>
                <span>{ollama_msg}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if available_models:
            model_found = any(model_name in m for m in available_models)
            if model_found:
                st.markdown(
                    f"""
                    <div class="status-badge status-online">
                        <span class="status-dot" style="background-color: #06B6D4; box-shadow: 0 0 8px #06B6D4;"></span>
                        <span>Model '{model_name}' active</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="status-badge status-warning">
                        <span class="status-dot" style="background-color: #F59E0B; box-shadow: 0 0 8px #F59E0B;"></span>
                        <span>Model '{model_name}' not found</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"""
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: -6px; margin-bottom: 10px; padding-left: 10px;">
                        Run: <code style="background: rgba(255,255,255,0.05); color: #F8FAFC; padding: 2px 4px; border-radius: 4px;">ollama pull {model_name}</code>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            f"""
            <div class="status-badge status-offline">
                <span class="status-dot" style="background-color: #EF4444; box-shadow: 0 0 8px #EF4444;"></span>
                <span>{ollama_msg}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    sidebar_section_header("Source Feed", '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>')
    video_url = st.text_input("YouTube URL or Video ID")
    if st.button("Load Video"):
        if not video_url or not video_url.strip():
            st.markdown(
                f"""
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                    {get_error_message("empty_url")}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            load_video(video_url.strip(), model_name)

    sidebar_section_header("Analysis Tools", '<ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path>')
    if st.button("Summary"):
        if st.session_state.vector_store is None:
            st.markdown(
                """
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                    Load a video first.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            with st.spinner("Generating summary…"):
                try:
                    st.session_state.last_output = generate_summary(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                            {e}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    if st.button("Key Topics"):
        if st.session_state.vector_store is None:
            st.markdown(
                """
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                    Load a video first.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            with st.spinner("Extracting topics…"):
                try:
                    st.session_state.last_output = generate_key_topics(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                            {e}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    if st.button("Quiz"):
        if st.session_state.vector_store is None:
            st.markdown(
                """
                <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                    Load a video first.
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            with st.spinner("Generating quiz…"):
                try:
                    st.session_state.last_output = generate_quiz(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                            {e}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    sidebar_section_header("System Metrics", '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>')
    st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 8px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 12px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #94A3B8;">Chunks Indexed</span>
                <span style="font-weight: 600; color: #F8FAFC;">{st.session_state.num_chunks}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                <span style="color: #94A3B8;">Total Characters</span>
                <span style="font-weight: 600; color: #F8FAFC;">{len(st.session_state.transcript)}</span>
            </div>
            {"".join(f'<div style="display: flex; justify-content: space-between; font-size: 0.85rem;"><span style="color: #94A3B8;">Video ID</span><span style="font-weight: 600; color: #06B6D4; font-family: monospace;">{st.session_state.video_id}</span></div>' if st.session_state.video_id else "")}
        </div>
        """,
        unsafe_allow_html=True
    )


# ── Q&A ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; margin-top: 12px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        <span style="font-size: 1.2rem; font-weight: 600; color: #F8FAFC;">Ask a Question</span>
    </div>
    """,
    unsafe_allow_html=True
)
question = st.text_input("Your question about the video")
if st.button("Ask"):
    if not question or not question.strip():
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                {get_error_message("empty_question")}
            </div>
            """,
            unsafe_allow_html=True
        )
    elif st.session_state.vector_store is None:
        st.markdown(
            """
            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                Load a video first.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        with st.spinner("Thinking…"):
            try:
                answer = answer_question(
                    question, st.session_state.vector_store, model_name
                )
                st.session_state.last_output = answer
                st.session_state.history.append((question, answer))
            except RuntimeError as e:
                msg = str(e)
                err_msg = get_error_message("ollama_not_running") if "Ollama" in msg else msg
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                        {err_msg}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.session_state.last_error = msg
            except Exception as e:
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 10px 14px; margin-top: 10px; font-size: 0.85rem; color: #EF4444;">
                        {e}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.session_state.last_error = str(e)


# ── Output ────────────────────────────────────────────────────────────────────
if st.session_state.last_output:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 24px; margin-bottom: 12px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            <span style="font-size: 1.1rem; font-weight: 600; color: #F8FAFC;">Analysis Result</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div class="glass-card" style="margin-top: 0;">
            <div style="color: #F8FAFC; font-size: 1rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state.last_output}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

if st.session_state.history:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 24px; margin-bottom: 12px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span style="font-size: 1.1rem; font-weight: 600; color: #F8FAFC;">Chat History</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for q, a in reversed(st.session_state.history[-5:]):
        st.markdown(
            f"""
            <div class="chat-bubble chat-bubble-user">
                <div class="chat-header">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    <span>User</span>
                </div>
                <div>{q}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div class="chat-bubble chat-bubble-assistant">
                <div class="chat-header">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>
                    <span>Assistant</span>
                </div>
                <div>{a}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.last_error:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 8px; margin-top: 24px; margin-bottom: 12px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            <span style="font-size: 1.1rem; font-weight: 600; color: #EF4444;">Last Error</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.code(st.session_state.last_error)

st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 8px; margin-top: 28px; margin-bottom: 12px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        <span style="font-size: 1.1rem; font-weight: 600; color: #F8FAFC;">Transcript Preview (first 1000 chars)</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.code(st.session_state.transcript[:1000] or "No transcript loaded.")
