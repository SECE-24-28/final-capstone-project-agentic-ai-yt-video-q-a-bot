# 🎥 YouTube Video Q&A Chatbot

A powerful AI-powered chatbot for asking questions about YouTube videos using local LLMs. Extract transcripts, create semantic embeddings, and get intelligent answers powered by Ollama, LangChain, and FAISS.

## ✨ Features

### Core Features
- **Ask Questions About Videos**: Get accurate answers based on video transcripts
- **Semantic Search**: FAISS vector database for intelligent context retrieval
- **Local AI Processing**: Uses Ollama for privacy-focused inference
- **Dark Modern UI**: Beautiful Streamlit interface with responsive design
- **Chat History**: Keep track of your questions and answers
- **Error Handling**: Graceful handling of network issues and edge cases

### Analysis Tools
- **📝 Generate Summaries**: Automatic video summarization
- **🏷️ Extract Key Topics**: Identify main concepts covered
- **❓ Generate Quiz**: Create quiz questions from video content

### Smart Features
- **Streaming**: Real-time answer generation
- **Caching**: Session-based caching for performance optimization
- **Multi-format URLs**: Supports all YouTube URL formats
- **Configurable Models**: Switch between different Ollama models
- **Transcript Statistics**: Word count, chunk count, reading time

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.10+ |
| **LLM** | Ollama (Local) |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Vector Store** | FAISS |
| **Text Processing** | LangChain |
| **Transcript API** | youtube-transcript-api |

## 📋 Requirements

### System Requirements
- Python 3.10 or higher
- Ollama installed and running locally
- 4GB+ RAM recommended
- 2GB disk space for models

### Python Packages
See `requirements.txt` for complete list:
```
streamlit==1.40.1
langchain==0.2.14
langchain-community==0.2.14
langchain-ollama==0.1.2
faiss-cpu==1.8.0
youtube-transcript-api==0.6.2
sentence-transformers==3.0.1
torch==2.2.1
requests==2.32.3
ollama==0.2.1
pydantic==2.8.2
```

## 🚀 Quick Start

### 1. Install Ollama
Download from [https://ollama.ai](https://ollama.ai) and install for your OS.

### 2. Start Ollama Service
```bash
# On macOS/Linux
ollama serve

# On Windows
# Run Ollama from Start Menu or Command Prompt
ollama serve
```

### 3. Pull a Model
```bash
ollama pull llama3
# Or other models:
# ollama pull llama2
# ollama pull mistral
# ollama pull neural-chat
```

### 4. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Run the Application
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Basic Q&A
1. **Load Video**: Paste a YouTube URL in the "Enter YouTube URL" field
2. **Wait**: The app will fetch and process the transcript
3. **Ask Questions**: Type your question and click "Ask"
4. **Get Answers**: Receive AI-generated answers based on video content

### URL Formats Supported
```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/embed/VIDEO_ID
https://www.youtube.com/watch?v=VIDEO_ID&t=XXs
```

### Analysis Tools

#### Generate Summary
- Click "📝 Generate Summary" in the Analysis tab
- Get a 3-4 paragraph summary of the main points

#### Extract Key Topics
- Click "🏷️ Extract Topics" in the Analysis tab
- Receive a bullet-point list of key concepts

#### Generate Quiz
- Click "❓ Generate Quiz" in the Analysis tab
- Get 3 multiple-choice questions with answers

## 📁 Project Structure

```
youtube-chatbot/
├── app.py                 # Main Streamlit application
├── chatbot.py            # Core chatbot logic and RAG pipeline
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration

### Model Selection
Change the default model in the sidebar:
- **llama3** (default) - Balanced performance and quality
- **llama2** - Faster, slightly less capable
- **mistral** - High performance
- **neural-chat** - Optimized for conversations

### Vector Store Settings
Edit in `chatbot.py`:
```python
chunk_size=1000        # Size of text chunks
chunk_overlap=200      # Overlap between chunks
k=3                   # Number of chunks to retrieve
```

### Ollama Connection
Default: `http://localhost:11434`

To use a remote Ollama instance, modify:
```python
base_url="http://remote-server:11434"
```

## 📊 Module Documentation

### chatbot.py

#### `extract_video_id(url: str) -> Optional[str]`
Extracts YouTube video ID from various URL formats.

#### `get_transcript(video_id: str) -> Optional[str]`
Fetches transcript using YouTube Transcript API.

#### `create_vector_store(text: str) -> Tuple[FAISS, int]`
Creates FAISS vector store with embeddings.

#### `retrieve_relevant_chunks(question: str, vector_store: FAISS, k: int) -> str`
Retrieves top k relevant chunks for a question.

#### `answer_question(question: str, vector_store: FAISS, model_name: str) -> str`
Generates answer using RAG pipeline.

#### `generate_summary(vector_store: FAISS, model_name: str) -> str`
Generates video summary.

#### `extract_key_topics(vector_store: FAISS, model_name: str) -> str`
Extracts key topics from video.

#### `generate_quiz(vector_store: FAISS, model_name: str, num_questions: int) -> str`
Generates quiz questions.

### utils.py

#### `is_valid_youtube_url(url: str) -> bool`
Validates YouTube URL format.

#### `get_error_message(error_type: str) -> str`
Returns user-friendly error messages.

#### `count_words(text: str) -> int`
Counts words in text.

#### `calculate_reading_time(text: str) -> str`
Calculates estimated reading time.

## ⚙️ Performance Optimization

### Caching
- Transcripts are cached per session
- Embeddings are cached after first creation
- Session state preserves data during interaction

### Best Practices
- **Chunk Size**: 1000 characters provides good balance
- **Chunk Overlap**: 200 characters for context continuity
- **Embedding Model**: all-MiniLM-L6-v2 is fast and accurate
- **Video Length**: Works best with 5-60 minute videos

### Memory Usage
- FAISS: ~500MB for typical video
- Embeddings: ~1-2MB per video
- Total: ~2-3GB RAM for full operation

## 🐛 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Ollama is not running" | Ollama service not started | Run `ollama serve` |
| "Model not found" | Model not pulled | Run `ollama pull llama3` |
| "No transcript found" | Video has no captions | Try another video |
| "Slow responses" | Large transcript or slow model | Use a faster model |
| "Connection refused" | Wrong Ollama URL | Check Ollama is running on correct port |

### Check Ollama Status
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# List available models
ollama list

# Test with a quick command
ollama run llama3 "hello"
```

### Debugging
Enable verbose logging:
```python
# In app.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔐 Privacy & Security

- **Local Processing**: All processing happens on your machine
- **No Cloud Upload**: Data never sent to external services
- **No Storage**: Transcripts are not permanently stored
- **Open Source**: Review code for security

## 📈 Performance Metrics

Typical performance on standard hardware (M1 MacBook/RTX 3060):

| Operation | Time | Model |
|-----------|------|-------|
| Transcript Fetch | 2-5s | Network dependent |
| Embedding Creation | 5-15s | Video length dependent |
| Q&A Response | 3-10s | Model & context dependent |
| Summary Generation | 10-20s | Model & context dependent |

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with hot reload
streamlit run app.py --logger.level=debug
```

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Web framework
- [LangChain](https://python.langchain.com/) - LLM framework
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [youtube-transcript-api](https://github.com/jderose9/youtube-transcript-api) - Transcript extraction

## 📧 Support

For issues and questions:
1. Check the Troubleshooting section above
2. Review error messages carefully
3. Verify Ollama is running
4. Check your internet connection

## 🚀 Future Enhancements

- [ ] Multi-video comparison
- [ ] Custom model fine-tuning
- [ ] Export conversation as PDF
- [ ] Bookmark important answers
- [ ] Translation support
- [ ] Custom prompt templates
- [ ] API endpoint for external tools
- [ ] Database storage of conversations

---

**Happy questioning! 🎥🤖**

Built with ❤️ using Streamlit, LangChain, and Ollama
