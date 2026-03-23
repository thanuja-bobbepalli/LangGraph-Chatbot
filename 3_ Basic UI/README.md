# LangGraph with Streamlit - Building Interactive AI Interfaces

## 🎯 Overview

This folder demonstrates how to build **interactive chatbot UIs** using **Streamlit** with LangGraph backends. You'll learn:
- **Frontend-backend separation** (Streamlit UI + LangGraph core)
- **Session state management** (maintaining conversation history)
- **Real-time streaming** (showing LLM responses as they generate)
- **Multi-threaded execution** (concurrent processing)
- **User experience optimization** (chat interfaces, message display)

---

## 📚 Core Concepts

### 1. **Frontend vs Backend Architecture**

```
┌─────────────────────────────┐
│   FRONTEND (streamlit_*.py) │
│  - UI components           │
│  - Chat history display    │
│  - User input handling     │
│  - Session management      │
└──────────────┬──────────────┘
               │ (invoke)
               ↓
┌─────────────────────────────┐
│  BACKEND (langgraph_*.py)   │
│  - Graph definition        │
│  - LLM integration         │
│  - State management        │
│  - Checkpointing          │
└─────────────────────────────┘
```

### 2. **Streamlit Basics**

Streamlit is a Python framework for building data apps and dashboards:

```python
import streamlit as st

# Display text
st.write("Hello, World!")

# Get user input
user_input = st.chat_input("Type your message")

# Display in chat format
with st.chat_message("user"):
    st.write(user_input)
```

### 3. **Session State - Persistent Data Within a Session**

Streamlit reruns scripts from top to bottom on every interaction. Session state maintains data across reruns:

```python
import streamlit as st

# Initialize session state (runs once)
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Access and modify
st.session_state['message_history'].append({'role': 'user', 'content': 'Hi'})

# Persists across reruns!
```

**How Session State Works:**
```
User types "Hello"
          ↓
Script reruns from top to bottom
          ↓
Session state values preserved
          ↓
Can use 'st.rerun()' to manually trigger rerun
```

### 4. **LangGraph Backend Integration**

The backend handles the AI logic:

```python
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# Backend is already compiled with checkpointer
CONFIG = {
    'configurable': {
        'thread_id': 'thread-1'
    }
}

# Use it from frontend
response = chatbot.invoke(
    {'messages': [HumanMessage(content=user_input)]},
    config=CONFIG
)
```

### 5. **Streaming vs Polling**

#### Polling (Basic - This Folder)
```python
response = chatbot.invoke(input)  # Wait for complete response
display(response)                  # Show entire response at once
```

#### Streaming (Advanced - Folder with "streaming")
```python
for chunk in chatbot.stream(input):  # Get chunks as they arrive
    display(chunk)                    # Show incrementally
```

---

## 🔧 How It Works (Step-by-Step)

### Backend Setup (`langgraph_backend.py`)

#### Step 1: Define State
```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

#### Step 2: Create Chat Node
```python
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)  # Call LLM
    return {"messages": [response]}
```

#### Step 3: Build and Compile Graph
```python
graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

checkpointer = InMemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)
```

**Key Point:** Backend is compiled once with checkpointer for memory.

### Frontend Setup (`streamlit_frontend.py`)

#### Step 1: Initialize Session State
```python
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = 'thread-1'
```

#### Step 2: Display Chat History
```python
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])
```

#### Step 3: Get User Input
```python
user_input = st.chat_input('Type your message')

if user_input:
    # Add to history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })
    
    # Display
    with st.chat_message('user'):
        st.write(user_input)
```

#### Step 4: Get LLM Response
```python
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

response = chatbot.invoke(
    {'messages': [HumanMessage(content=user_input)]},
    config=CONFIG
)

# Extract response
ai_message = response['messages'][-1].content

# Add to history
st.session_state['message_history'].append({
    'role': 'assistant',
    'content': ai_message
})

# Display
with st.chat_message('assistant'):
    st.write(ai_message)
```

---

## 📋 Complete Working Example

### Backend Code (`langgraph_backend.py`)
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# Initialize LLM
llm = HuggingFaceEndpoint(repo_id="deepseek-ai/DeepSeek-V3.2")
llm = ChatHuggingFace(llm=llm)

# Define State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Define Node
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Build Graph
graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# Compile with persistence
checkpointer = InMemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)
```

### Frontend Code (`streamlit_frontend.py`)
```python
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# Configuration
CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# Initialize session state
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Display title
st.title("🤖 LangGraph Chatbot")

# Display chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Get user input
user_input = st.chat_input('Type your message here...')

if user_input:
    # Add user message to history
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })
    
    # Display user message
    with st.chat_message('user'):
        st.write(user_input)
    
    # Get response from backend
    response = chatbot.invoke(
        {'messages': [HumanMessage(content=user_input)]},
        config=CONFIG
    )
    
    # Extract AI message
    ai_text = response['messages'][-1].content
    
    # Add to history
    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_text
    })
    
    # Display AI message
    with st.chat_message('assistant'):
        st.write(ai_text)

# Optional: Clear chat button
if st.sidebar.button('Clear Chat'):
    st.session_state['message_history'] = []
    st.rerun()
```

---

## 🎨 Streamlit Components Used

| Component | Purpose | Example |
|-----------|---------|---------|
| `st.write()` | Display text/data | `st.write("Hello")` |
| `st.chat_message()` | Display chat bubbles | `with st.chat_message('user'):` |
| `st.chat_input()` | Get user message | `user_input = st.chat_input('...')` |
| `st.session_state` | Persist data | `st.session_state['key'] = value` |
| `st.rerun()` | Trigger script rerun | `st.rerun()` |
| `st.sidebar` | Side panel | `st.sidebar.button('...')` |
| `st.title()` | Page title | `st.title("My App")` |

---

## 📊 Data Flow Diagram

```
User Types Message
        ↓
st.chat_input() captures it
        ↓
Add to st.session_state['message_history']
        ↓
Display with st.chat_message('user')
        ↓
Backend: chatbot.invoke(user_message)
        ↓
LLM processes with full context
        ↓
Backend returns response
        ↓
Add to st.session_state['message_history']
        ↓
Display with st.chat_message('assistant')
        ↓
Script reruns (session_state preserved!)
```

---

## 🚀 Advanced Features

### 1. **Streaming Responses** (`streamlit_frontend_streaming.py`)
```python
with st.chat_message('assistant'):
    message_placeholder = st.empty()
    full_response = ""
    
    for chunk in chatbot.stream(input_data):
        full_response += chunk
        message_placeholder.write(full_response)
```

### 2. **Threading** (`streamlit_frontend_threading_updated.py`)
```python
import threading

def fetch_response():
    response = chatbot.invoke(...)
    st.session_state['response'] = response

thread = threading.Thread(target=fetch_response)
thread.start()
thread.join()
```

### 3. **Error Handling**
```python
try:
    response = chatbot.invoke(...)
except Exception as e:
    st.error(f"Error: {str(e)}")
```

### 4. **Loading Indicators**
```python
with st.spinner('Thinking...'):
    response = chatbot.invoke(...)
```

---

## 🔑 Session State Best Practices

✅ **DO:**
```python
# Initialize with default values
if 'counter' not in st.session_state:
    st.session_state['counter'] = 0

# Use consistent keys
st.session_state['user_name'] = "John"
```

❌ **DON'T:**
```python
# Don't modify local variables and expect persistence
local_var = 0
local_var += 1  # Lost on rerun!

# Don't assume key exists without checking
value = st.session_state['undefined_key']  # KeyError!
```

---

## 💡 Tips for Better UX

1. **Loading States**: Show "thinking..." indicator
2. **Error Messages**: Display failures gracefully
3. **Clear Chat Button**: Let users start fresh
4. **Scrolling**: Auto-scroll to latest message
5. **Message Formatting**: Use markdown for better display
6. **Responsive Design**: Works on mobile/desktop

---

## 🔗 Files Included

| File | Purpose |
|------|---------|
| `langgraph_backend.py` | Backend with LLM + State |
| `streamlit_frontend.py` | Basic chat UI |
| `streamlit_frontend_streaming.py` | With streaming responses |
| `streamlit_frontend_threading_updated.py` | With threading |
| `streamlit_frontend_threding.py` | (typo version) |

---

## 🏃 How to Run

```bash
# Install dependencies
pip install streamlit langgraph langchain-core

# Run frontend
streamlit run streamlit_frontend.py
```

Streamlit app opens at: `http://localhost:8501`

---

## 📈 UpgradeandNext Steps

1. **Add sidebar controls** (model selection, parameters)
2. **Implement real streaming** (token-by-token display)
3. **Add conversation export** (save chats to file)
4. **Multi-user support** (different threads per user)
5. **Response regeneration** (retry last response)
6. **Message editing** (edit previous messages)

---

## ✅ What You've Learned

- ✓ Streamlit basics (components, layout)
- ✓ Session state management
- ✓ Frontend-backend separation
- ✓ Integrating LangGraph with UI
- ✓ Chat message display
- ✓ User input handling
- ✓ Error handling and UX

---

## 🔗 Related Folders

- **Folder 1 (Intro)**: Core LangGraph concepts
- **Folder 2 (Persistence)**: Multi-node workflows
- **Folder 4 (Database)**: Production-ready with SQLite
