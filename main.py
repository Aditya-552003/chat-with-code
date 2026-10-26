import os
import re
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import PromptTemplate, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.readers.github import GithubClient, GithubRepositoryReader

load_dotenv()

APP_REPO_URL = "https://github.com/Aditya-552003/chat-with-code"
EMBEDDING_MODEL = "BAAI/bge-small-en"


def parse_github_url(url: str) -> tuple[str, str, str]:
    """Parse a GitHub repository URL, including branches with slashes."""
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() not in {
        "github.com",
        "www.github.com",
    }:
        raise ValueError("Enter a valid https://github.com/owner/repository URL.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("The URL must include both an owner and repository name.")

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", owner) or not re.fullmatch(
        r"[A-Za-z0-9_.-]+", repo
    ):
        raise ValueError("The repository URL contains an invalid owner or name.")

    branch = "main"
    if len(parts) >= 4 and parts[2] == "tree":
        branch = "/".join(parts[3:])
    elif len(parts) > 2:
        raise ValueError("Use a repository URL or a branch URL containing /tree/<branch>.")

    return owner, repo, branch


@st.cache_resource(show_spinner=False)
def get_embedding_model():
    """Load the embedding model once per app process."""
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)


@st.cache_resource(show_spinner=False, ttl=1800, max_entries=8)
def load_github_data(github_token: str, owner: str, repo: str, branch: str):
    client = GithubClient(github_token or None)
    reader = GithubRepositoryReader(
        client,
        owner=owner,
        repo=repo,
        filter_file_extensions=None,
        verbose=False,
        concurrent_requests=5,
    )
    return reader.load_data(branch=branch)


def build_query_engine(docs):
    # The index is session-owned, avoiding cross-session sharing of repository content.
    index = VectorStoreIndex.from_documents(docs, embed_model=get_embedding_model())
    llm = GoogleGenAI(model="gemini-2.5-flash")
    return index.as_query_engine(
        llm=llm,
        similarity_top_k=5,
        streaming=False,
    )


def answer_question(query_text: str, query_engine) -> str:
    prompt = PromptTemplate(
        "You are a helpful senior software engineer explaining a code repository. "
        "Answer using the supplied repository context. If the answer is not in the "
        "context, say what is missing rather than inventing details. Use concise "
        "sections and code examples when useful.\n\n"
        "Repository context:\n---------------------\n{context_str}\n"
        "---------------------\nQuestion: {query_str}\nAnswer:"
    )
    query_engine.update_prompts({"response_synthesizer:text_qa_template": prompt})
    return str(query_engine.query(query_text))


def reset_repository():
    st.session_state.docs = None
    st.session_state.query_engine = None
    st.session_state.repo_info = None
    st.session_state.messages = []


def main():
    st.set_page_config(
        page_title="Chat with Code",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 1.8rem; padding-bottom: 3rem;}
        [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.18);}
        .hero-subtitle {font-size: 1.05rem; opacity: .78; margin-top: -.6rem;}
        div[data-testid="stChatMessage"] {border-radius: 14px; padding: .7rem 1rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if not os.getenv("GEMINI_API_KEY"):
        st.error("Gemini API key not found. Add GEMINI_API_KEY to your .env file or deployment secrets.")
        st.stop()

    for key, default in {
        "messages": [],
        "docs": None,
        "query_engine": None,
        "repo_info": None,
        "repo_url_input": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    header_left, header_right = st.columns([4, 1])
    with header_left:
        st.title("💬 Chat with Code")
        st.markdown(
            '<p class="hero-subtitle">Understand any public GitHub codebase with AI-powered, context-aware answers.</p>',
            unsafe_allow_html=True,
        )
    with header_right:
        st.link_button("⭐ Star project", APP_REPO_URL, use_container_width=True)

    with st.sidebar:
        st.subheader("📦 Connect a repository")
        st.caption("Paste a public repository URL. You can also specify a branch.")
        with st.form("repository_form", clear_on_submit=False):
            repo_url = st.text_input(
                "GitHub URL",
                value=st.session_state.repo_url_input,
                placeholder="https://github.com/owner/repository",
                help="For a branch, use https://github.com/owner/repository/tree/branch-name",
            )
            load_clicked = st.form_submit_button(
                "Load repository", type="primary", use_container_width=True
            )

        if load_clicked:
            st.session_state.repo_url_input = repo_url
            try:
                owner, repo, branch = parse_github_url(repo_url)
                with st.status("Loading and indexing repository…", expanded=True) as status:
                    st.write(f"Repository: {owner}/{repo}")
                    st.write(f"Branch: {branch}")
                    github_token = os.getenv("GITHUB_TOKEN", "")
                    docs = load_github_data(github_token, owner, repo, branch)
                    if not docs:
                        raise ValueError("No readable files were found on this branch.")
                    st.write(f"Loaded {len(docs)} document chunks. Building search index…")
                    engine = build_query_engine(docs)
                    status.update(label="Repository ready", state="complete", expanded=False)

                st.session_state.docs = docs
                st.session_state.query_engine = engine
                st.session_state.repo_info = {
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "url": f"https://github.com/{owner}/{repo}/tree/{branch}",
                }
                st.session_state.messages = []
                st.success("Repository loaded. Ask your first question!")
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error("Could not load this repository. Check that it exists, the branch is correct, and GitHub is reachable.")
                with st.expander("Technical details"):
                    st.code(f"{type(exc).__name__}: {exc}")

        if st.session_state.repo_info:
            info = st.session_state.repo_info
            st.divider()
            st.success(f"Connected: {info['owner']}/{info['repo']}")
            st.caption(f"Branch: {info['branch']}")
            st.link_button("Open on GitHub ↗", info["url"], use_container_width=True)
            if st.button("Switch repository", use_container_width=True):
                reset_repository()
                st.rerun()

        st.divider()
        st.caption("💡 Tip: Ask about architecture, entry points, functions, dependencies, bugs, or how to add a feature.")
        st.caption("GitHub token is optional for public repositories, but can help with API rate limits.")

    if st.session_state.repo_info:
        info = st.session_state.repo_info
        st.markdown(f"#### Exploring {info['owner']}/{info['repo']}")
        st.caption(f"Branch: {info['branch']} · {len(st.session_state.docs)} documents indexed")
        starter_cols = st.columns(3)
        starters = [
            ("🏗️ Architecture", "Explain the project architecture and the main execution flow."),
            ("🧭 Find entry points", "Which files are the main entry points, and what does each do?"),
            ("🛠️ Improvement ideas", "Review this codebase and suggest the highest-impact improvements."),
        ]
        for col, (label, starter_prompt) in zip(starter_cols, starters):
            with col:
                if st.button(label, use_container_width=True, key=f"starter_{label}"):
                    st.session_state.pending_prompt = starter_prompt
                    st.rerun()
    else:
        st.info("👈 Load a GitHub repository from the sidebar to begin.")
        with st.container(border=True):
            st.markdown("### Your codebase, ready to explore")
            c1, c2, c3 = st.columns(3)
            c1.markdown("**🏗️ Understand**\n\nExplore architecture, modules, and execution flow.")
            c2.markdown("**🔎 Investigate**\n\nAsk about functions, dependencies, or potential bugs.")
            c3.markdown("**🚀 Improve**\n\nGet grounded suggestions for refactoring and new features.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.messages:
        export = "\n\n".join(
            f"## {'You' if m['role'] == 'user' else 'Chat with Code'}\n\n{m['content']}"
            for m in st.session_state.messages
        )
        download_col, clear_col = st.columns([1, 1])
        with download_col:
            st.download_button(
                "⬇️ Export conversation",
                data=export,
                file_name="chat-with-code-conversation.md",
                mime="text/markdown",
            )
        with clear_col:
            if st.button("🗑️ Clear conversation", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    pending_prompt = st.session_state.pop("pending_prompt", None)
    prompt = st.chat_input(
        "Ask a question about the codebase…",
        disabled=st.session_state.query_engine is None,
    )
    prompt = prompt or pending_prompt

    if prompt:
        if st.session_state.query_engine is None:
            st.warning("Load a repository before asking questions.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Reading the code and preparing an answer…"):
                    response = answer_question(prompt, st.session_state.query_engine)
                st.markdown(response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as exc:
                st.error("I couldn't generate an answer this time. Please try again.")
                with st.expander("Technical details"):
                    st.code(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
