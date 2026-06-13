import re
import urllib.parse
from typing import Tuple, List

from youtube_transcript_api import YouTubeTranscriptApi

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama


def extract_video_id(url: str) -> str:
    if not url or not isinstance(url, str):
        raise ValueError("Invalid YouTube URL or id provided.")

    url = url.strip()

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    if not re.match(r"https?://", url, re.IGNORECASE):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    hostname = (parsed.hostname or "").lower()

    if hostname.endswith("youtu.be"):
        vid = parsed.path.lstrip("/").split("?")[0].split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            return vid

    if hostname.endswith("youtube.com") or hostname.endswith("youtube-nocookie.com"):
        qs = urllib.parse.parse_qs(parsed.query)
        if qs.get("v"):
            vid = qs["v"][0]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
                return vid

        path_parts = [p for p in parsed.path.split("/") if p]
        for i, part in enumerate(path_parts):
            if part in ("embed", "v", "shorts") and i + 1 < len(path_parts):
                cand = path_parts[i + 1]
                if re.fullmatch(r"[A-Za-z0-9_-]{11}", cand):
                    return cand

    raise ValueError(f"Could not extract video ID from: {url}")


def get_transcript(video_id: str) -> str:
    if not video_id or not isinstance(video_id, str):
        raise ValueError("Invalid video id.")

    print(f"[DEBUG] Fetching transcript for video_id: {video_id}")

    def format_time(seconds: float) -> str:
        s = int(seconds)
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h > 0:
            return f"{h}:{m:02d}:{sec:02d}"
        else:
            return f"{m}:{sec:02d}"

    def get_snippet_data(snippet) -> Tuple[str, float]:
        if isinstance(snippet, dict):
            return snippet.get("text", ""), float(snippet.get("start", 0.0))
        text = getattr(snippet, "text", "")
        start = getattr(snippet, "start", 0.0)
        return str(text), float(start)

    def process_snippets(snippets) -> str:
        parts = []
        last_time = -999.0
        for snippet in snippets:
            t, start = get_snippet_data(snippet)
            if not t:
                continue
            if start - last_time >= 30.0:
                parts.append(f"[{format_time(start)}] {t}")
                last_time = start
            else:
                parts.append(t)
        return " ".join(parts)

    # v1.x API: fetch_transcript returns a FetchedTranscript object, iterate it
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        text = process_snippets(fetched)
        if not text.strip():
            raise RuntimeError("Transcript is empty.")
        print(f"[DEBUG] Transcript source: youtube-transcript-api v1.x fetch()")
        print(f"[DEBUG] Transcript length: {len(text)} chars")
        return text
    except Exception as e1:
        print(f"[DEBUG] fetch() failed: {e1}")

    # Fallback: list_transcripts then fetch manually
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_manually_created_transcript(["en"])
        except Exception:
            pass
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(["en"])
            except Exception:
                pass
        if transcript is None:
            # grab first available
            for t in transcript_list:
                transcript = t
                break
        if transcript is None:
            raise RuntimeError("No transcript available for this video.")

        data = transcript.fetch()
        text = process_snippets(data)
        if not text.strip():
            raise RuntimeError("Transcript is empty.")
        print(f"[DEBUG] Transcript source: list_transcripts fallback")
        return text
    except Exception as e2:
        print(f"[DEBUG] list_transcripts fallback failed: {e2}")
        raise RuntimeError(
            f"Transcript retrieval failed for video ID '{video_id}'.\n"
            f"Primary error: {e1}\n"
            f"Fallback error: {e2}\n"
            "Suggested fix: Ensure the video has captions enabled, or try a different video."
        )


def create_vector_store(text: str) -> Tuple[FAISS, int]:
    if not text or not text.strip():
        raise ValueError("No transcript text to build vector store.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_text(text)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(texts, embeddings)
    return vector_store, len(texts)


def _llm_invoke(model_name: str, prompt: str) -> str:
    llm = Ollama(model=model_name)
    try:
        resp = llm.invoke(prompt)
    except Exception as e:
        raise RuntimeError(f"Ollama LLM error (model={model_name}): {e}")
    return resp.strip() if isinstance(resp, str) else str(resp).strip()


def _get_context(vector_store: FAISS, query: str, k: int) -> str:
    docs = vector_store.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content for d in docs)


def _get_all_context(vector_store: FAISS) -> str:
    ordered_docs = []
    if hasattr(vector_store, "index_to_docstore_id") and isinstance(vector_store.index_to_docstore_id, dict):
        for i in range(len(vector_store.index_to_docstore_id)):
            doc_id = vector_store.index_to_docstore_id.get(i)
            if doc_id:
                doc = vector_store.docstore.search(doc_id)
                if doc:
                    ordered_docs.append(doc.page_content)
    else:
        docs = list(vector_store.docstore._dict.values())
        ordered_docs = [d.page_content for d in docs]
    return "\n\n---\n\n".join(ordered_docs)


def answer_question(question: str, vector_store: FAISS, model_name: str = "llama3") -> str:
    if not question or not question.strip():
        raise ValueError("Question is empty.")
    context = _get_context(vector_store, question, k=5)
    if not context:
        return "The information is not available in the video transcript."
    prompt = (
        "Answer the QUESTION using ONLY the CONTEXT below. "
        "If the answer is not in the CONTEXT, reply: The information is not available in the video transcript.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nAnswer concisely."
    )
    return _llm_invoke(model_name, prompt)


def generate_summary(vector_store: FAISS, model_name: str = "llama3") -> str:
    context = _get_all_context(vector_store)
    prompt = (
        "Summarize the CONTENT below in 3-6 sentences.\n\n"
        f"CONTENT:\n{context}"
    )
    return _llm_invoke(model_name, prompt)


def generate_key_topics(vector_store: FAISS, model_name: str = "llama3") -> str:
    context = _get_all_context(vector_store)
    prompt = (
        "List 6-12 key topics as bullet points from the CONTENT below.\n\n"
        f"CONTENT:\n{context}"
    )
    return _llm_invoke(model_name, prompt)


def generate_quiz(vector_store: FAISS, model_name: str = "llama3") -> str:
    context = _get_all_context(vector_store)
    prompt = (
        "Generate a 5-question multiple-choice quiz (question + 4 options + correct answer) "
        "based ONLY on the CONTENT below.\n\n"
        f"CONTENT:\n{context}"
    )
    return _llm_invoke(model_name, prompt)


def generate_qa_pairs(vector_store: FAISS, model_name: str = "llama3") -> str:
    context = _get_all_context(vector_store)
    prompt = (
        "Generate 6 question-and-answer pairs from the CONTENT below.\n"
        "Format each pair exactly as:\n"
        "Q: <question>\n"
        "A: <answer>\n\n"
        "Use only information from the CONTENT. Be concise.\n\n"
        f"CONTENT:\n{context}"
    )
    return _llm_invoke(model_name, prompt)


def generate_mcq_quiz(vector_store: FAISS, model_name: str = "llama3", num_questions: int = 7) -> str:
    context = _get_all_context(vector_store)
    prompt = (
        f"Generate exactly {num_questions} multiple-choice questions from the CONTENT below.\n"
        "Return ONLY valid JSON — no explanation, no markdown, no code fences.\n"
        "Use this exact JSON structure:\n"
        '[{"question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answer": "A"}]\n'
        "Rules:\n"
        "- answer must be exactly one of: A, B, C, D\n"
        "- all 4 options must be present\n"
        "- base questions only on the CONTENT\n\n"
        f"CONTENT:\n{context}"
    )
    return _llm_invoke(model_name, prompt)


def timestamp_to_seconds(ts: str) -> int:
    parts = list(map(int, ts.split(":")))
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return 0


def answer_question_with_sources(question: str, vector_store: FAISS, model_name: str = "llama3") -> Tuple[str, List[str]]:
    if not question or not question.strip():
        raise ValueError("Question is empty.")
    
    docs = vector_store.similarity_search(question, k=5)
    
    timestamps = []
    for d in docs:
        matches = re.findall(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]", d.page_content)
        if matches:
            timestamps.append(matches[0])
            
    seen = set()
    unique_timestamps = []
    for ts in timestamps:
        if ts not in seen:
            seen.add(ts)
            unique_timestamps.append(ts)
            
    context = "\n\n---\n\n".join(d.page_content for d in docs)
    if not context:
        return "The information is not available in the video transcript.", []
        
    prompt = (
        "Answer the QUESTION using ONLY the CONTEXT below. "
        "If the answer is not in the CONTEXT, reply: The information is not available in the video transcript.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{question}\n\nAnswer concisely."
    )
    
    answer = _llm_invoke(model_name, prompt)
    return answer, unique_timestamps


def translate_text(text: str, target_language: str, model_name: str = "llama3") -> str:
    if not text or not text.strip():
        return ""
    prompt = (
        f"Translate the following TEXT to {target_language}. "
        "Maintain the exact formatting, paragraph breaks, and bullet points. "
        "Do not add any preamble, explanations, or notes. Output ONLY the translation.\n\n"
        f"TEXT:\n{text}"
    )
    return _llm_invoke(model_name, prompt)

