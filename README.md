# LangGraph Chatbot - Complete Learning Guide

A progressive learning project demonstrating how to build AI chatbots using **LangGraph**, from basic concepts to production-ready applications with tools, databases, and advanced integrations.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Key Concepts](#key-concepts)
7. [Folder Guide](#folder-guide)
8. [Quick Start](#quick-start)
9. [Running Each Example](#running-each-example)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

This project is a **step-by-step learning journey** through LangGraph, starting from basic chatbot concepts and progressing to enterprise-level features. Each folder builds upon the previous one, introducing new concepts and capabilities:

- Folder 1-2: Foundational concepts (state management, persistence)
- Folder 3-4: UI integration and database persistence
- Folder 5: Production monitoring with LangSmith
- Folder 6-8: Advanced features (tools, MCPs, RAG)

**What is LangGraph?**
LangGraph is a framework for building stateful, agentic AI applications with explicit control flow. It enables you to create sophisticated multi-step workflows where the LLM (language model) acts as a decision-maker, and tools/functions perform the actual work.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | LangGraph (LangChain ecosystem) |
| **LLM** | Google Gemini, HuggingFace, or other providers |
| **Frontend** | Streamlit |
| **Database** | SQLite |
| **Vector Store** | FAISS (for RAG) |
| **Monitoring** | LangSmith |
| **Protocol** | MCP (Model Context Protocol) |
| **Language** | Python 3.9+ |

---

## Project Structure

```
LangGraph_Chatbot/
│
├── 1_Intro/
│   ├── 1_basic_chatbot.ipynb       # Jupyter notebook - Start here!
│   └── README.md
│
├── 2_persistant/
│   ├── persistance_example.ipynb    # Advanced state management
│   └── README.md
│
├── 3_ Basic UI/
│   ├── langgraph_backend.py         # Backend logic
│   ├── streamlit_frontend.py        # Basic UI
│   ├── streamlit_frontend_streaming.py
│   ├── streamlit_frontend_threading_updated.py
│   └── README.md
│
├── 4_ Chatbot with database/
│   ├── backend.py                   # LangGraph + SQLite
│   ├── streamlit_frontend_withdb.py # Enhanced UI
│   ├── streamlit_frontend_withdb_updated.py
│   └── README.md
│
├── 5_Langsmith Integration with LangGraph/
│   ├── backend.py                   # With tracing
│   ├── streamlit_frontend.py
│   ├── Instructions.txt
│   └── sample_outputs/              # Example traces
│
├── 6_Chatbot_with tools/
│   ├── Backend_with_tools.py        # Tool integration
│   ├── streamlit_frontend_withTools.py
│   ├── requirements.txt
│   ├── instruction README.md
│   └── sample_outputs/
│
├── 7_Chatbot with MCPs/
│   ├── chatbot_backend_with_mcp.py  # MCP integration
│   ├── chatbot_frontend_with_mcp.py
│   ├── chatbot_async.py
│   ├── main.py
│   └── README.md
│
├── 8_ Chatbot with RAG as a tool/
│   ├── backend_rag_tool.py          # RAG + Tools + Database
│   ├── frontent_with_Ragtool.py     # Advanced UI
│   ├── requirements.txt
│   └── README.md
│
└── requirements.txt                 # Global dependencies
```

---

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip or conda package manager
- 2GB+ free disk space
- Internet connection (for API calls)

### Required API Keys
You'll need the following API keys depending on which examples you run:

1. **GOOGLE_API_KEY** (for Gemini LLM)
   - Get it from: https://ai.google.dev/
   - Used in folders 1-5

2. **LANGSMITH_API_KEY** (optional, for tracing)
   - Get it from: https://smith.langchain.com/
   - Used in folder 5

3. **HUGGINGFACE_API_TOKEN** (for some models)
   - Get it from: https://huggingface.co/settings/tokens
   - Used in folder 8

---

## Installation

### Step 1: Clone the Repository
```bash
cd c:\Users\Dell\Desktop\LangGraph_Chatbot
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install global requirements first
pip install -r requirements.txt

# Some folders have their own requirements
# For example, folder 6:
cd "6_Chatbot_with tools"
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_google_api_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=chatbot-project
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
```

---

## Key Concepts

### 1. StateGraph - Building Workflows

A StateGraph is a directed graph where:
- **Nodes** = Functions that process data
- **Edges** = Control flow between nodes
- **State** = Shared data passed between nodes

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(ChatState)          # Define state structure
graph.add_node('chat_node', chat_func) # Add processing node
graph.add_edge(START, 'chat_node')     # Connect START → node
graph.add_edge('chat_node', END)       # Connect node → END
```

### 2. State Management with TypedDict

State is the "memory" of your workflow:

```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str
```

### 3. Checkpointers - Persistence

Checkpointers save workflow state at each step:

```python
# In-memory (development)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Database (production)
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
conn = sqlite3.connect('chatbot.db')
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
# ... add nodes and edges ...
app = graph.compile(checkpointer=checkpointer)
```

### 4. Thread Management - Multiple Conversations

Each conversation is a separate "thread":

```python
# Thread 1: User A
config1 = {'configurable': {'thread_id': 'user-a-123'}}

# Thread 2: User B  
config2 = {'configurable': {'thread_id': 'user-b-456'}}

# They have completely separate conversation histories
response1 = app.invoke({'messages': [...]}, config1)
response2 = app.invoke({'messages': [...]}, config2)
```

### 5. Tools - Extended Capabilities

Tools allow the LLM to interact with external systems:

```python
# Define a tool
def calculate(expression: str) -> str:
    """Evaluate a math expression"""
    return str(eval(expression))

# Bind to LLM
tools = [calculate]
llm_with_tools = llm.bind_tools(tools)

# LLM now can call this tool when needed
```

### 6. RAG - Retrieval Augmented Generation

RAG enables the AI to reference documents:

```python
# Load documents
docs = pdf_loader.load_and_split()

# Create embeddings
embeddings = HuggingFaceEmbeddings()

# Store in vector database
vectorstore = FAISS.from_documents(docs, embeddings)

# Retrieve and use in prompts
retrieved_docs = vectorstore.similarity_search(query)
```

---

## Folder Guide

### Folder 1: Basic Chatbot (1_Intro/)

**What you'll learn:**
- StateGraph fundamentals
- Basic node creation
- State management with TypedDict
- LLM integration
- Memory-based checkpointing

**Key files:**
- `1_basic_chatbot.ipynb` - Interactive Jupyter notebook

**To run:**
```bash
cd 1_Intro
jupyter notebook 1_basic_chatbot.ipynb
```

**Output examples:**
```
User: Hello, what's your name?
Bot: I'm Claude, an AI assistant. How can I help?

User: Tell me a joke
Bot: Why did the LLM go to school? To improve its context window!
```

---

### Folder 2: Persistence & Multi-Node Workflows (2_persistant/)

**What you'll learn:**
- Advanced state management
- Multi-node sequential workflows
- State checkpointing
- Time travel debugging (accessing historical states)
- Thread management

**Key files:**
- `persistance_example.ipynb`

**To run:**
```bash
cd 2_persistant
jupyter notebook persistance_example.ipynb
```

**Key difference from Folder 1:**
```
Folder 1: Stateless (forgets previous messages)
Folder 2: Stateful (remembers full conversation history)
```

---

### Folder 3: Streamlit UI with LangGraph Backend (3_ Basic UI/)

**What you'll learn:**
- Frontend-backend separation
- Streamlit basics and session state
- Real-time streaming of LLM responses
- Multi-threaded execution
- User experience optimization

**Key files:**
- `langgraph_backend.py` - Backend logic
- `streamlit_frontend.py` - Basic chat interface
- `streamlit_frontend_streaming.py` - Streaming responses
- `streamlit_frontend_threading_updated.py` - Concurrent processing

**To run:**
```bash
cd "3_ Basic UI"

# Basic version
streamlit run streamlit_frontend.py

# Streaming version
streamlit run streamlit_frontend_streaming.py

# Threading version
streamlit run streamlit_frontend_threading_updated.py
```

Opens at: `http://localhost:8501`

**Features:**
- Chat interface with message history
- Real-time response streaming
- Session-based conversation persistence

---

### Folder 4: Chatbot with SQLite Database (4_ Chatbot with database/)

**What you'll learn:**
- Database persistence (SQLite)
- Production-ready architecture
- Multi-conversation management
- Thread retrieval and enumeration
- Advanced Streamlit UI with sidebar navigation

**Key files:**
- `backend.py` - LangGraph with SqliteSaver
- `streamlit_frontend_withdb.py` - UI with thread management
- `streamlit_frontend_withdb_updated.py` - Enhanced version

**To run:**
```bash
cd "4_ Chatbot with database"
streamlit run streamlit_frontend_withdb.py
```

**Key differences from Folder 3:**
```
Folder 3: MemorySaver  (data lost when app restarts)
Folder 4: SqliteSaver  (data persists permanently)
```

**Features:**
- Create multiple chat threads
- Switch between conversations
- Rename conversations
- Delete old conversations
- Persistent conversation history

---

### Folder 5: LangSmith Integration (5_Langsmith Integration with LangGraph/)

**What you'll learn:**
- LangSmith tracing setup
- Monitoring LLM calls
- Debugging workflows with traces
- Performance analysis
- Production observability

**Key files:**
- `backend.py` - Same as Folder 4, but with tracing
- `streamlit_frontend.py`
- `Instructions.txt` - Setup guide

**To run:**
```bash
# Step 1: Set up LangSmith
# Add LANGSMITH_API_KEY to .env

# Step 2: Run the app
cd "5_Langsmith Integration with LangGraph"
streamlit run streamlit_frontend.py
```

**What happens:**
- Every LLM call is logged to LangSmith
- View traces at: https://smith.langchain.com/
- Monitor performance, tokens, latency, costs

**LangSmith Dashboard shows:**
- Input/output for each call
- Token usage
- Response time
- Error tracking
- Cost analysis

---

### Folder 6: Chatbot with Tools (6_Chatbot_with tools/)

**What you'll learn:**
- Tool definition and binding
- Agentic workflows
- Tool calling and execution
- Error handling for tools
- Multi-step reasoning

**Key files:**
- `Backend_with_tools.py` - Tool integration
- `streamlit_frontend_withTools.py` - UI with tool display

**To run:**
```bash
cd "6_Chatbot_with tools"
streamlit run streamlit_frontend_withTools.py
```

**Tools example:**
```python
# Available tools
- Calculator: Perform math operations
- Web Search: Search the internet
- Stock Lookup: Get real-time stock prices
```

**Usage example:**
```
User: What is the stock price of Apple?
Bot: [Calls stock_lookup tool] AAPL is $251.64

User: Multiply that by 100
Bot: [Calls calculator tool] 100 * 251.64 = 25,164
```

**Key difference from Folder 5:**
```
Folder 5: LLM decides what to say
Folder 6: LLM decides AND calls tools to act
```

---

### Folder 7: Chatbot with MCPs (7_Chatbot with MCPs/)

**What you'll learn:**
- Model Context Protocol (MCP)
- Decoupled tool architecture
- Tool servers and clients
- Async/await patterns
- Scalable tool system

**Key files:**
- `chatbot_backend_with_mcp.py` - MCP client
- `chatbot_frontend_with_mcp.py` - UI
- `chatbot_async.py` - Async implementation
- `main.py` - Entry point

**To run:**
```bash
cd "7_Chatbot with MCPs"
python main.py

# In another terminal
cd "7_Chatbot with MCPs"
streamlit run chatbot_frontend_with_mcp.py
```

**MCP Advantages:**
- Tools run as separate servers
- Independent scaling
- Easy tool updates
- Clean separation of concerns

**Architecture:**
```
Streamlit UI
    ↓
MCP Client (Backend)
    ↓
Tool Servers (External processes)
```

---

### Folder 8: Chatbot with RAG as a Tool (8_ Chatbot with RAG as a tool/)

**What you'll learn:**
- Retrieval Augmented Generation (RAG)
- Vector embeddings and similarity search
- PDF document loading and processing
- FAISS vector store
- Combining RAG with tools
- Complete production application

**Key files:**
- `backend_rag_tool.py` - RAG + tools + database
- `frontent_with_Ragtool.py` - Advanced UI
- `requirements.txt` - Dependencies

**To run:**
```bash
cd "8_ Chatbot with RAG as a tool"
pip install -r requirements.txt
streamlit run frontent_with_Ragtool.py
```

**Features:**
- Upload PDF documents
- Ask questions about your docs
- Real-time web search
- Stock price lookup
- Calculator tool
- Thread-based conversation management

**RAG Workflow:**
```
User: "What does page 3 say?"
    ↓
1. Find similar content in uploaded PDFs
2. Pass to LLM as context
3. LLM generates answer based on document
```

**Example usage:**
```
Upload: annual_report.pdf
Ask: "What were the Q4 earnings?"
Bot: [Retrieves from PDF] Q4 earnings were $50M
```

---

## Quick Start

### For Beginners - Start with Folder 1

```bash
# Navigate to folder 1
cd 1_Intro

# Open Jupyter notebook
jupyter notebook 1_basic_chatbot.ipynb

# Run through all cells to understand basics
```

### For UI Developers - Start with Folder 3

```bash
# Navigate to folder 3
cd "3_ Basic UI"

# Run Streamlit app
streamlit run streamlit_frontend.py

# Try streaming version
streamlit run streamlit_frontend_streaming.py
```

### For Production - Start with Folder 4

```bash
# Navigate to folder 4
cd "4_ Chatbot with database"

# Run with database persistence
streamlit run streamlit_frontend_withdb.py

# Check chatbot.db for stored conversations
```

### For Advanced Features - Try Folders 6-8

```bash
# Tools and agentic workflows
cd "6_Chatbot_with tools"
streamlit run streamlit_frontend_withTools.py

# MCPs and decoupled architecture
cd "7_Chatbot with MCPs"
streamlit run chatbot_frontend_with_mcp.py

# Complete RAG + tools + database
cd "8_ Chatbot with RAG as a tool"
streamlit run frontent_with_Ragtool.py
```

---

## Running Each Example

### Example 1: Basic Chatbot

```bash
cd 1_Intro
jupyter notebook 1_basic_chatbot.ipynb

# Or run Python directly
python -c "
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

# Create your chatbot...
"
```

### Example 2: Persistence

```bash
cd 2_persistant
jupyter notebook persistance_example.ipynb
```

### Example 3: Streamlit UI

```bash
cd "3_ Basic UI"
streamlit run streamlit_frontend.py

# Open browser to http://localhost:8501
# Type messages and see responses stream in real-time
```

### Example 4: Database Persistence

```bash
cd "4_ Chatbot with database"
streamlit run streamlit_frontend_withdb.py

# Features:
# - Left sidebar shows conversation threads
# - Create new chats
# - Switch between conversations
# - Rename chats
# - Delete old conversations
```

### Example 5: LangSmith Tracing

```bash
# 1. Add LANGSMITH_API_KEY to .env
# 2. Set LANGSMITH_PROJECT in .env

cd "5_Langsmith Integration with LangGraph"
streamlit run streamlit_frontend.py

# 3. Visit https://smith.langchain.com/ to see traces
```

### Example 6: Tools Integration

```bash
cd "6_Chatbot_with tools"
streamlit run streamlit_frontend_withTools.py

# Ask questions that require tools:
# - "What's the stock price of AAPL?"
# - "Calculate 150 * 25"
# - "Search for latest AI news"
```

### Example 7: MCPs

```bash
cd "7_Chatbot with MCPs"

# Terminal 1: Run backend
python main.py

# Terminal 2: Run Streamlit
streamlit run chatbot_frontend_with_mcp.py
```

### Example 8: RAG + Tools

```bash
cd "8_ Chatbot with RAG as a tool"
streamlit run frontent_with_Ragtool.py

# 1. Click "Upload PDF" button
# 2. Select your PDF file
# 3. Ask questions about the document
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langgraph'"

**Solution:**
```bash
pip install langgraph langchain langchain-google-genai streamlit
```

### Issue: "GOOGLE_API_KEY not found"

**Solution:**
```bash
# Create .env file in root directory
echo GOOGLE_API_KEY=your_key_here > .env

# Or on Windows
(echo GOOGLE_API_KEY=your_key_here) > .env
```

### Issue: "Port 8501 already in use"

**Solution:**
```bash
# Kill existing Streamlit process
# Or specify different port
streamlit run streamlit_frontend.py --server.port 8502
```

### Issue: "SQLite database locked"

**Solution:**
This happens when using threading. The backend already handles this with `check_same_thread=False`.
If you get this error:

```python
# In backend.py, ensure:
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
```

### Issue: "LANGSMITH_API_KEY error"

**Solution:**
```bash
# Make sure key is in .env
cat .env

# Restart Streamlit
# This refreshes environment variables
```

### Issue: "PDF upload not working"

**Solution:**
```bash
# Ensure PyPDF is installed
pip install pypdf

# Check PDF file size (should be < 25MB)
# Try different PDF format
```

### Issue: "FAISS import error"

**Solution:**
```bash
pip install faiss-cpu
# or
pip install faiss-gpu
```

### Issue: "Out of memory error"

**Solution:**
- Use smaller models
- Process PDFs in smaller chunks
- Reduce batch size

---

## Project Roadmap

### Completed
- Basic chatbot (Folder 1)
- Persistence (Folder 2)
- Streamlit UI (Folder 3)
- Database integration (Folder 4)
- LangSmith tracing (Folder 5)
- Tools integration (Folder 6)
- MCPs integration (Folder 7)
- RAG implementation (Folder 8)

### Possible Extensions
- Langchain agents
- Multi-modal inputs (voice, images)
- Fine-tuning support
- Cost optimization
- Advanced security (user auth)
- Kubernetes deployment
- REST API layer
- Caching optimizations

---

## Best Practices

### 1. Always Use Virtual Environments
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Keep API Keys Secure
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use environment variables
GOOGLE_API_KEY=xxx streamlit run app.py
```

### 3. Test Locally First
```bash
# Start with Folder 1 (Jupyter)
# Then move to Folder 3 (Streamlit)
# Then add complexity (database, tools, etc.)
```

### 4. Monitor Token Usage
```python
# Check token consumption in LangSmith
# Optimize prompts to reduce tokens
# Consider token budgets for production
```

### 5. Database Maintenance
```bash
# Periodically clean old threads
# Back up chatbot.db before major updates
# Monitor database file size
```

---

## Additional Resources

### LangGraph
- Documentation: https://langraph.dev/
- GitHub: https://github.com/langchain-ai/langgraph

### LangChain
- Documentation: https://python.langchain.com/
- Community: https://discord.gg/langchain

### Streamlit
- Documentation: https://docs.streamlit.io/
- Gallery: https://streamlit.io/gallery

### LangSmith
- Platform: https://smith.langchain.com/
- Docs: https://docs.smith.langchain.com/

### Google Generative AI
- API: https://ai.google.dev/
- Documentation: https://cloud.google.com/docs/generative-ai

---

## Contributing

Found a bug or want to improve the project?

1. Update the relevant folder's code
2. Test locally
3. Document changes in the folder's README

---

## License

This project is provided as-is for educational purposes.

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the README in each folder
3. Check LangGraph documentation
4. Examine example outputs in `sample_outputs/` directories

---

## Summary

This project provides a comprehensive learning path for building AI chatbots:

| Folder | Focus | Complexity | Duration |
|--------|-------|-----------|----------|
| 1 | Basics | Beginner | 1 hour |
| 2 | Persistence | Beginner | 1 hour |
| 3 | UI/Streamlit | Intermediate | 2 hours |
| 4 | Database | Intermediate | 2 hours |
| 5 | Monitoring | Intermediate | 1 hour |
| 6 | Tools | Advanced | 3 hours |
| 7 | MCPs | Advanced | 3 hours |
| 8 | RAG | Advanced | 4 hours |

**Total estimated learning time: 17 hours**

Start with Folder 1 and progress sequentially for the best learning experience!
