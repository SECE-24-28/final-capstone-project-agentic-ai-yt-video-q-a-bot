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

st.set_page_config(page_title="YouTube Video Q&A Chatbot", layout="wide")

st.markdown(
    """
    <style>
    .reportview-container { background: #0e1117; color: #e6edf3; }
    .stButton>button, .stTextInput>div>div>input {
        background-color: #111827; color: #e6edf3;
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
        st.error(f"{get_error_message('invalid_url')} — {e}")
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
            st.success(f"✅ Video loaded — {num_chunks} chunks indexed.")
        except RuntimeError as e:
            msg = str(e)
            st.error("❌ Transcript retrieval failed.")
            st.info(f"Video ID: `{video_id}`")
            st.code(msg)
            st.session_state.last_error = msg
        except Exception as e:
            msg = str(e)
            st.error(f"❌ Unexpected error: {msg}")
            st.info(f"Video ID: `{video_id}`")
            st.session_state.last_error = msg


# ── Layout ───────────────────────────────────────────────────────────────────
st.title("🎥 YouTube Video Q&A Chatbot")

with st.sidebar:
    st.header("⚙️ Controls")
    model_name = st.text_input("Ollama model", value="llama3")

    # Diagnostics
    ollama_ok, ollama_msg, available_models = check_ollama(model_name)
    if ollama_ok:
        st.success(f"🟢 {ollama_msg}")
        if available_models:
            model_found = any(model_name in m for m in available_models)
            if model_found:
                st.success(f"🟢 Model `{model_name}` available.")
            else:
                st.warning(f"⚠️ Model `{model_name}` not found. Run: `ollama pull {model_name}`")
                st.write("Available:", available_models)
    else:
        st.error(f"🔴 {ollama_msg}")

    st.markdown("---")
    video_url = st.text_input("YouTube URL or Video ID")
    if st.button("▶️ Load Video"):
        if not video_url or not video_url.strip():
            st.error(get_error_message("empty_url"))
        else:
            load_video(video_url.strip(), model_name)

    st.markdown("---")
    st.markdown("**🔧 Analysis Tools**")
    if st.button("📝 Summary"):
        if st.session_state.vector_store is None:
            st.error("Load a video first.")
        else:
            with st.spinner("Generating summary…"):
                try:
                    st.session_state.last_output = generate_summary(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.error(str(e))

    if st.button("🏷️ Key Topics"):
        if st.session_state.vector_store is None:
            st.error("Load a video first.")
        else:
            with st.spinner("Extracting topics…"):
                try:
                    st.session_state.last_output = generate_key_topics(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.error(str(e))

    if st.button("❓ Quiz"):
        if st.session_state.vector_store is None:
            st.error("Load a video first.")
        else:
            with st.spinner("Generating quiz…"):
                try:
                    st.session_state.last_output = generate_quiz(
                        st.session_state.vector_store, model_name
                    )
                except Exception as e:
                    st.error(str(e))

    st.markdown("---")
    st.markdown("**📊 Stats**")
    st.write(f"Chunks: `{st.session_state.num_chunks}`")
    st.write(f"Transcript chars: `{len(st.session_state.transcript)}`")
    if st.session_state.video_id:
        st.write(f"Video ID: `{st.session_state.video_id}`")


# ── Q&A ───────────────────────────────────────────────────────────────────────
st.subheader("💬 Ask a Question")
question = st.text_input("Your question about the video")
if st.button("🔍 Ask"):
    if not question or not question.strip():
        st.error(get_error_message("empty_question"))
    elif st.session_state.vector_store is None:
        st.error("Load a video first.")
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
                st.error(get_error_message("ollama_not_running") if "Ollama" in msg else msg)
                st.session_state.last_error = msg
            except Exception as e:
                st.error(str(e))
                st.session_state.last_error = str(e)

# ── Output ────────────────────────────────────────────────────────────────────
if st.session_state.last_output:
    st.markdown("---")
    st.markdown("**Result:**")
    st.write(st.session_state.last_output)

if st.session_state.history:
    st.markdown("---")
    st.markdown("**Chat History:**")
    for q, a in reversed(st.session_state.history[-5:]):
        st.markdown(f"**Q:** {q}")
        st.markdown(f"**A:** {a}")
        st.markdown("---")

if st.session_state.last_error:
    st.markdown("**Last error:**")
    st.code(st.session_state.last_error)

st.markdown("---")
st.markdown("**Transcript Preview (first 1000 chars)**")
st.code(st.session_state.transcript[:1000] or "No transcript loaded.")
