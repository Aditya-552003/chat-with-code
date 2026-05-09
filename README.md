# Chat with Code

A Streamlit application that allows you to load any public GitHub repository and interactively ask questions about its codebase. Powered by LlamaIndex and Gemini 2.5 Flash.

## Features

- **Load GitHub Repositories**: Directly fetch and index files from any public GitHub repo.
- **AI-Powered Code Analysis**: Ask detailed questions about the codebase and get accurate, context-aware answers.
- **Download Responses**: Easily export your conversations as Markdown files.
- **Fast & Responsive**: Built with Streamlit for a seamless UI experience, with caching for repository loading and index building to ensure fast interactions.

## Prerequisites

- Python 3.10 or higher
- A [Google Gemini API Key](https://aistudio.google.com/)
- A [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) (optional but recommended for higher rate limits when reading repositories)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/chat-with-code.git
   cd chat-with-code
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install .
   ```

4. **Set up your environment variables:**
   Create a `.env` file in the root of the project and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here
   ```

## Usage

1. **Run the Streamlit application:**
   ```bash
   python -m streamlit run main.py
   ```

2. **Interact with the app:**
   - Enter the URL of a GitHub repository in the sidebar (e.g., `https://github.com/owner/repo`).
   - Click "Load Repository".
   - Start chatting with the codebase!

## Built With

- [Streamlit](https://streamlit.io/) - The web framework used.
- [LlamaIndex](https://www.llamaindex.ai/) - Data framework for connecting custom data sources to LLMs.
- [Google Gemini](https://ai.google.dev/) - The LLM used for generating answers.

## License

This project is licensed under the MIT License.
