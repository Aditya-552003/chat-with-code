# Chat with Code 🚀

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2015-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-4285F4?style=flat&logo=google&logoColor=white)](https://aistudio.google.com)
[![LlamaIndex](https://img.shields.io/badge/RAG-LlamaIndex-purple?style=flat)](https://www.llamaindex.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Chat with Code** is a production-grade full-stack web application that allows you to connect any public GitHub repository and interactively analyze its architecture, workflows, and logic using Retrieval-Augmented Generation (RAG).

Powered by **Next.js 15**, **FastAPI**, **Google Gemini 2.5 Flash**, **BAAI/bge-small-en dense embeddings**, and **LlamaIndex**.

---

## 🌟 Key Features

- **Decoupled Architecture**: High-performance FastAPI backend paired with a modern, responsive Next.js 15 App Router frontend.
- **GitHub Repository Indexer**: Seamlessly fetch any public repository and branch via the GitHub REST API with branch-aware path parsing.
- **AST & Semantic Code Chunking**: Intelligent code splitters respecting syntactic boundaries (functions, classes, blocks) rather than naive character slicing.
- **Dense Vector Search**: Powered by `BAAI/bge-small-en` (384-dimensional dense embeddings) and in-memory vector indexing for lightning-fast similarity lookups.
- **Real-Time Streaming Responses**: Token-by-token Server-Sent Events (SSE) streaming with live cursor animation.
- **Grounded Source Citations**: Every answer provides referenced code snippets, line numbers, relevance scores, and direct GitHub permalinks.
- **Interactive Repository Explorer**: Inspect indexed files, vector chunk distributions, and branch metadata.
- **Export Conversations**: One-click export of chat sessions as cleanly formatted Markdown documentation.
- **Modern UI & Dark Mode**: Glassmorphism design system built with Tailwind CSS, Lucide icons, and light/dark theme persistence.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Next.js 15 UI                         │
│  (React 19, Tailwind CSS, Lucide Icons, Markdown Renderer)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE Stream
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
├──────────────────────────────┬──────────────────────────────┤
│  • Rate Limiting & Validation│  • Background Task Jobs      │
│  • Health & Diagnostics      │  • Error Shielding           │
└──────────────┬───────────────┴──────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐┌─────────────────────────────┐
│       GitHub Service         ││       RAG & AI Pipeline     │
│  • Repository Loader         ││  • AST Code Splitter        │
│  • Tree & Content Fetcher    ││  • BAAI/bge-small-en Embeds │
│  • File Extension Filtering  ││  • FAISS / VectorStore      │
└──────────────────────────────┘│  • Gemini 2.5 Flash LLM     │
                                └─────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **UI Library**: [React 19](https://react.dev/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Code Highlighting**: `react-syntax-highlighter` (Prism One-Dark)
- **Markdown Rendering**: `react-markdown` + `remark-gfm`

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **RAG & Orchestration**: [LlamaIndex](https://www.llamaindex.ai/)
- **LLM**: Google Gemini 2.5 Flash via `llama-index-llms-google-genai`
- **Embeddings**: `BAAI/bge-small-en` via HuggingFace
- **Vector Storage**: In-Memory Vector Store

---

## 🚀 Quickstart

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ (tested on Node 20 & 24)
- **Google Gemini API Key** ([Get key](https://aistudio.google.com/))
- **GitHub Token** (*optional*, recommended for higher API rate limits)

---

### Method 1: Local Development

#### 1. Clone the repository
```bash
git clone https://github.com/Aditya-552003/chat-with-code.git
cd chat-with-code
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `backend/.env` with your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_github_token_optional
FRONTEND_ORIGIN=http://localhost:3000
```

Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```
Backend API will be running at `http://localhost:8000`. Swagger documentation available at `http://localhost:8000/docs`.

#### 3. Frontend Setup
In a new terminal:
```bash
cd frontend

# Install packages
npm install

# Start Next.js development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### Method 2: Docker Compose

Run both the FastAPI backend and Next.js frontend with a single command:

```bash
# Set your Gemini API key in your environment
export GEMINI_API_KEY="your_gemini_api_key_here"

# Build and start services
docker-compose up --build
```

Access the frontend at `http://localhost:3000` and API at `http://localhost:8000`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check & configuration diagnostics |
| `POST` | `/api/repositories/load` | Queue and start indexing a GitHub repository |
| `GET` | `/api/repositories/jobs/{id}` | Poll background indexing job progress |
| `GET` | `/api/repositories/{id}` | Retrieve repository metadata & chunk statistics |
| `POST` | `/api/chat` | Non-streaming question answering with citations |
| `POST` | `/api/chat/stream` | Server-Sent Events (SSE) token streaming |
| `GET` | `/api/conversations/{id}` | Fetch conversation history |
| `DELETE` | `/api/conversations/{id}` | Clear conversation session |
| `GET` | `/api/conversations/{id}/export` | Export conversation as Markdown |

---

## 🔒 Security & Best Practices

- **Origin Validation**: Strict CORS middleware configured for frontend origins.
- **Input Sanitization**: Pydantic schemas validate URLs, branch names, and query payloads.
- **Rate Limit Resilience**: Automatic exponential backoff when contacting external APIs.
- **Safe Citations**: Sanitized file paths and validated line numbers preventing path traversal.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
