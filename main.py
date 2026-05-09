import streamlit as st
import os
import re
from dotenv import load_dotenv

from llama_index.core import Settings, VectorStoreIndex, PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.github import GithubRepositoryReader, GithubClient

# Load environment variables
load_dotenv()


# -------------------------------
# Helper: Parse GitHub URL
# -------------------------------
def parse_github_url(url):
    pattern = r"https?://github\.com/([^/]+)/([^/]+)(?:/tree/([^/]+))?"
    match = re.match(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub repository URL")
    owner, repo, branch = match.groups()
    return owner, repo, branch if branch else "main"


# -------------------------------
# Load GitHub Repo Data
# -------------------------------
@st.cache_resource
def load_github_data(github_token, owner, repo, branch="main"):
    github_client = GithubClient(github_token)
    loader = GithubRepositoryReader(
        github_client,
        owner=owner,
        repo=repo,
        filter_file_extensions=None,
        verbose=False,
        concurrent_requests=5,
    )
    return loader.load_data(branch=branch)


# -------------------------------
# Build Index (cached 🚀)
# -------------------------------
@st.cache_resource
def build_index(docs):
    return VectorStoreIndex.from_documents(docs)


# -------------------------------
# RAG Function
# -------------------------------
def run_rag_completion(query_text: str, docs) -> str:
    llm = GoogleGenAI(model="gemini-2.5-flash")  

    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en"
    )

    index = build_index(docs)
    query_engine = index.as_query_engine(similarity_top_k=5, streaming=True)

    qa_prompt_tmpl = PromptTemplate(
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information, please answer the query.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": qa_prompt_tmpl
    })

    response = query_engine.query(query_text)
    return str(response)


# -------------------------------
# Main App
# -------------------------------
def main():
    st.set_page_config(page_title="Chat with Code", layout="wide")

    # API key check
    if not os.getenv("GEMINI_API_KEY"):
        st.error("❌ Please set GEMINI_API_KEY in .env file")
        st.stop()

    @st.fragment
    def download_response(response: str):
        st.download_button(
            label="Download message",
            type="secondary",
            data=response,
            file_name="chatbot_response.md",
            mime="text/plain",
            icon=":material/download:",
        )

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "docs" not in st.session_state:
        st.session_state.docs = None

    # Header
    col1, col2, col5, col3, col4 = st.columns([3, 1, 1, 1, 1])
    with col1:
        st.title("🤖 Chat with Code")
    with col3:
        st.link_button("⭐ Star Repo", "https://github.com/Aditya-552003/hybrid-emotion-fastapi.git")
    with col4:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    st.caption("Powered by Gemini + LlamaIndex")

    # Sidebar
    with st.sidebar:
        st.subheader("GitHub Repository URL")
        repo_url = st.text_input("", placeholder="Enter repository URL")

        if st.button("Load Repository"):
            if repo_url:
                try:
                    github_token = os.getenv("GITHUB_TOKEN")
                    google_api_key = os.getenv("GEMINI_API_KEY")

                    if not github_token or not google_api_key:
                        st.error("Missing API keys")
                        st.stop()

                    owner, repo, branch = parse_github_url(repo_url)

                    with st.spinner("Loading repository..."):
                        st.session_state.docs = load_github_data(
                            github_token, owner, repo, branch
                        )

                    st.success("✓ Repository loaded successfully")

                except Exception:
                    st.error("Error loading repository. Check URL or API keys.")

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about the repository..."):
        if not st.session_state.docs:
            st.error("Please load a repository first")
            st.stop()

        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = run_rag_completion(
                        prompt, st.session_state.docs
                    )
                    st.markdown(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

                    download_response(response)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    raise e


if __name__ == "__main__":
    main()