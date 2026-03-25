# Multi-Utility Chatbot with LangGraph & PDF RAG

A powerful AI-driven chatbot built with **LangGraph**, **LangChain**, and **Streamlit** that combines document retrieval, web search, stock price lookup, and calculations in a single conversational interface.

## 🎯 Live Demo

**[Access the live app here](https://tha789-chatbot.streamlit.app/)**

## Features

- **PDF Upload & Retrieval (RAG)**
  - Upload PDF documents and ask questions about their content
  - Uses FAISS vector stores for efficient similarity search
  - Per-thread document management

- **Web Search**
  - Real-time web search using DuckDuckGo
  - Integrated into chatbot responses when relevant

- **Stock Price Lookup**
  - Get real-time stock prices using Alpha Vantage API
  - Query multiple stock symbols (e.g., AAPL, TSLA)

- **Calculator Tool**
  - Perform arithmetic operations (add, subtract, multiply, divide)
  - Integrated directly into chat

- **Multi-Thread Conversation Management**
  - Create unlimited chat threads
  - Rename conversations for easy organization
  - Delete threads to clean up
  - Persistent conversation history with SQLite

- **Advanced LLM**
  - Powered by Qwen2.5-7B-Instruct from HuggingFace
  - Intelligent tool selection and execution
  - Natural language understanding

## Project Structure

```
Chatbot/
├── backend_rag_tool.py          # LangGraph workflow, RAG pipeline, tools
├── frontent_with_Ragtool.py     # Streamlit UI and frontend
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (keep secret!)
├── .streamlit/
│   └── secrets.toml              # Streamlit secrets (for deployment)
├── chatbot.db                    # SQLite database (conversation history)
└── README.md                     # This file
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit |
| **LLM** | HuggingFace Qwen2.5-7B-Instruct |
| **Workflow** | LangGraph |
| **RAG/Vector Store** | FAISS + Sentence Transformers |
| **Document Processing** | PyPDF |
| **Search** | DuckDuckGo Search |
| **Persistence** | SQLite |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Internet connection
- HuggingFace API token

## Installation

### 1. Clone or Download the Project

```bash
cd Chatbot
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration & API Setup

### Local Development (.env file)

Create a `.env` file in the project root directory with your API credentials:

```env
# HuggingFace API Token (Required)
# Get it from: https://huggingface.co/settings/tokens
HUGGINGFACEHUB_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Stock Price API Key (Required for stock price tool)
# Get it from: https://www.alphavantage.co/
STOCK_PRICE_API=JIENSG24LKB220MQ
```

### Streamlit Deployment (Secrets Management)

For the **live Streamlit app**, API keys are stored securely in **Streamlit Secrets**:

#### How to Add Secrets to Your Streamlit App:

1. **Go to your Streamlit app dashboard**: [https://share.streamlit.io](https://share.streamlit.io)

2. **Select your app** and click on the **⚙️ Settings** button (top right)

3. **Click on "Secrets"** in the left sidebar

4. **Add your secrets** in the secrets editor (TOML format):

```toml
HUGGINGFACEHUB_API_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
STOCK_PRICE_API = "JIENSG24LKB220MQ"
```

5. **Click "Save"** - The app will automatically redeploy with the new secrets

#### Security Best Practices:

✅ **DO:**
- Use Streamlit's built-in secrets management
- Rotate API keys regularly
- Use environment-specific tokens
- Keep `.env` and `.streamlit/secrets.toml` in `.gitignore`

❌ **DON'T:**
- Commit `.env` files to Git
- Share API keys in code or documentation
- Use the same key across multiple environments
- Expose secrets in logs or error messages

## Usage

### Run Locally

```bash
streamlit run frontent_with_Ragtool.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Chatbot

1. **Start a New Chat**
   - Click "New Chat" in the sidebar to create a fresh conversation
   - Each chat gets a unique thread ID for persistent storage

2. **Upload a PDF**
   - Use the file uploader in the sidebar
   - The PDF will be split into chunks and indexed in FAISS
   - Document metadata shows filename, pages, and chunks

3. **Ask Questions**
   - Ask about PDF content: "What are the main topics discussed?"
   - Use tools: "What's the stock price of AAPL?"
   - Do calculations: "Add 50 and 25"
   - General queries: "Search for Python tutorials"

4. **Manage Conversations**
   - **✏️ Button**: Rename a thread
   - **🗑️ Button**: Delete a thread
   - Click thread title to load the conversation

## How It Works

### Architecture Flow

```
User Input (Streamlit)
    ↓
LangGraph Chat Node
    ↓
LLM with Tool Binding (Qwen2.5-7B)
    ↓
Tool Decision
├─ RAG Tool → FAISS Vector Search → PDF Content
├─ Search Tool → DuckDuckGo Search
├─ Stock Tool → Alpha Vantage API
└─ Calculator Tool → Math Operation
    ↓
Tool Execution & Response
    ↓
Message History Storage (SQLite)
    ↓
Display in Streamlit UI
```

### Key Components

**1. Backend (backend_rag_tool.py)**
- LangGraph state machine for chat workflow
- Tool definitions (RAG, search, stock, calculator)
- PDF ingestion and FAISS indexing
- SQLite checkpointing for conversation persistence
- Thread-based retriever management

**2. Frontend (frontent_with_Ragtool.py)**
- Streamlit UI with multi-thread management
- PDF upload and metadata display
- Message history rendering
- Real-time streaming of AI responses
- Thread CRUD operations (Create, Read, Update, Delete)

**3. Database (chatbot.db)**
- SQLite database storing all message history
- Automatic checkpointing for each chat turn
- Thread-based conversation isolation

## Requirements

All dependencies are listed in `requirements.txt`:

```
streamlit==1.55.0
langchain==1.2.13
langchain-community==0.4.1
langchain-core==1.2.20
langchain-huggingface==1.2.1
langgraph==1.1.3
langgraph-checkpoint-sqlite==3.0.3
sentence-transformers==5.3.0
faiss-cpu==1.13.2
pypdf==6.9.2
ddgs==9.11.4
aiosqlite==0.22.1
requests==2.32.5
python-dotenv==1.2.2
huggingface_hub==1.7.2
```

## API Keys Required

### 1. HuggingFace API Token (Required)
- Sign up: [https://huggingface.co](https://huggingface.co)
- Get token: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Used for: LLM inference (Qwen2.5-7B-Instruct)

### 2. Alpha Vantage API Key (Required for stock prices)
- Sign up: [https://www.alphavantage.co](https://www.alphavantage.co)
- Get free API key
- Used for: Real-time stock price lookups

## Troubleshooting

### **"No API token found"**
- Ensure `.env` file exists in the project root
- Check that `HUGGINGFACEHUB_API_TOKEN` is set correctly
- For Streamlit Cloud, verify secrets in app settings

### **"No document indexed for this chat"**
- Upload a PDF first using the sidebar uploader
- Wait for the indexing to complete

### **Slow responses**
- HuggingFace free tier has rate limits
- Consider upgrading to paid API access
- Response times are typically 10-30 seconds

### **SQLite "database is locked"**
- Ensure only one instance of the app is running
- Close the previous Streamlit session

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `HUGGINGFACEHUB_API_TOKEN` | Yes | HuggingFace API token for LLM | `hf_abc123xyz...` |
| `STOCK_PRICE_API` | Yes | Alpha Vantage API key | `JIENSG24LKB220MQ` |

## Deployment

### Streamlit Cloud

1. Push your code to GitHub (with `.env` in `.gitignore`)
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in the app settings (see **Configuration & API Setup** section)
5. Deploy!

### Other Cloud Platforms

For Heroku, AWS, Google Cloud, etc., ensure:
- Environment variables are set via platform settings
- SQLite database persistence is configured
- All dependencies from `requirements.txt` are installed

## Learn More

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FAISS Documentation](https://faiss.ai/)
- [HuggingFace Models](https://huggingface.co/models)

## License

[Add your license here if applicable]

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Contact

For questions or support, [add contact information here]

---

**Built with LangGraph, LangChain, and Streamlit**

Last Updated: March 2026
