# LangGraph with SQLite Database - Production-Ready Chatbot

## 🎯 Overview

This folder demonstrates **production-ready chatbot implementation** with:
- **Database persistence** (SQLite for state storage)
- **Multi-conversation management** (switch between chats)
- **Thread management** (unique ID per conversation)
- **Conversation history** (load/save/delete chats)
- **Rename conversations** (user-friendly titles)
- **Advanced Streamlit UI** (sidebar navigation, thread management)

This is the **most complete example** combining all previous concepts into a real application.

---

## 📚 Core Concepts

### 1. **Database Persistence vs Memory Persistence**

#### Memory (Folders 1-3)
```python
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()
# Data lost when app restarts ❌
```

#### Database (This Folder) ✅
```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect('chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
# Data persists even after restart ✅
```

**Comparison:**
| Feature | InMemorySaver | SqliteSaver |
|---------|---------------|------------|
| Restart persistence | ❌ Lost | ✅ Saved |
| Scalability | ❌ Limited | ✅ Good |
| Production ready | ⚠️ No | ✅ Yes |
| Setup complexity | ✅ Simple | ⚠️ Moderate |
| Performance | ✅ Fast | ✅ Very fast |

### 2. **SQLite - Lightweight Database**

SQLite is a file-based database stored as a single `.db` file:

```python
import sqlite3

# Connect to database (creates chatbot.db if not exists)
conn = sqlite3.connect(
    database='chatbot.db',
    check_same_thread=False  # Required for async/threading
)

# Now create SqliteSaver checkpointer
checkpointer = SqliteSaver(conn=conn)
```

**Database Schema (Auto-created by LangGraph):**
```
chatbot.db
├── threads (table)
│   ├── thread_id (primary key)
│   ├── checkpoint_id
│   ├── values (state as JSON)
│   └── created_at
```

### 3. **Thread Management**

Each conversation is a **separate thread** with unique ID:

```python
# Thread 1: Programming jokes
thread_1_config = {'configurable': {'thread_id': 'abc123'}}

# Thread 2: Python jokes  
thread_2_config = {'configurable': {'thread_id': 'xyz789'}}

# These have completely separate conversation histories!
```

### 4. **Retrieving All Threads**

Function to fetch all conversations from database:

```python
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        all_threads.add(thread_id)
    return list(all_threads)
```

**Usage:**
```python
threads = retrieve_all_threads()
# Returns: ['thread-1', 'thread-2', 'thread-3']
```

### 5. **Loading Conversation History**

Get all messages from a specific thread:

```python
def load_conversation(thread_id):
    config = {'configurable': {'thread_id': thread_id}}
    state = chatbot.get_state(config)
    return state.values.get('messages', [])
```

**Example:**
```python
messages = load_conversation('thread-1')
# Returns: [HumanMessage(...), AIMessage(...), ...]
```

### 6. **Conversation Titles**

Extract first user message as conversation title:

```python
def get_title_from_messages(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            return msg.content[:30]  # First 30 chars
    return "New Chat"
```

---

## 🔧 How It Works (Step-by-Step)

### Backend Setup (`backend.py`)

#### Step 1: Database Connection
```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect(
    database='chatbot.db',
    check_same_thread=False
)
```

#### Step 2: Create Checkpointer
```python
checkpointer = SqliteSaver(conn=conn)
```

#### Step 3: Build and Compile Graph
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)
```

#### Step 4: Thread Retrieval Function
```python
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config['configurable']['thread_id']
        all_threads.add(thread_id)
    return list(all_threads)
```

### Frontend Setup (`streamlit_frontend_withdb_updated.py`)

#### Step 1: Utility Functions
```python
import uuid

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id, "New Chat")
    st.session_state['message_history'] = []

def add_thread(thread_id, title="New Chat"):
    if not any(t["id"] == thread_id for t in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({
            "id": thread_id,
            "title": title
        })

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])
```

#### Step 2: Initialize Session State
```python
import streamlit as st
from backend import chatbot, retrieve_all_threads

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    threads = retrieve_all_threads()
    chat_threads = []
    
    for t in threads:
        messages = chatbot.get_state(config={'configurable': {'thread_id': t}}).values.get('messages', [])
        
        # Extract title from first user message
        title = "New Chat"
        for msg in messages:
            if isinstance(msg, HumanMessage):
                title = msg.content[:30]
                break
        
        chat_threads.append({"id": t, "title": title})
    
    st.session_state['chat_threads'] = chat_threads
```

#### Step 3: Sidebar UI with Thread Management
```python
st.sidebar.title('💬 Chatbot')

# New Chat Button
if st.sidebar.button('➕ New Chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('My Conversations')

# List all threads
for thread in st.session_state['chat_threads'][::-1]:  # Reverse to show newest first
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    
    # Load conversation button
    if col1.button(thread["title"], key=f"thread_{thread['id']}", use_container_width=True):
        st.session_state['thread_id'] = thread["id"]
        
        messages = load_conversation(thread["id"])
        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})
        
        st.session_state['message_history'] = temp_messages
    
    # Rename button (✏️)
    if col2.button("✏️", key=f"rename_{thread['id']}", use_container_width=True):
        st.session_state[f"rename_mode_{thread['id']}"] = True
    
    # Delete button (🗑️)
    if col3.button("🗑️", key=f"delete_{thread['id']}", use_container_width=True):
        st.session_state['chat_threads'] = [
            t for t in st.session_state['chat_threads']
            if t["id"] != thread["id"]
        ]
        if st.session_state['thread_id'] == thread["id"]:
            reset_chat()
        st.rerun()
```

#### Step 4: Chat Interface
```python
# Display message history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

# Get user input
user_input = st.chat_input('Type your message...')

if user_input:
    # Update thread title if first message
    for thread in st.session_state['chat_threads']:
        if thread["id"] == st.session_state["thread_id"] and thread["title"] == "New Chat":
            thread["title"] = user_input[:30]
    
    # Add user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    
    with st.chat_message('user'):
        st.write(user_input)
    
    # Get response
    config = {'configurable': {'thread_id': st.session_state['thread_id']}}
    response = chatbot.invoke(
        {'messages': [HumanMessage(content=user_input)]},
        config=config
    )
    
    ai_text = response['messages'][-1].content
    
    # Add AI message
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_text})
    
    with st.chat_message('assistant'):
        st.write(ai_text)
```

---

## 📋 Complete Data Flow Example

### Scenario: User has 3 conversations

```
Database (chatbot.db)
├── Thread "abc-1" → ["Hi", "Hello!", "How are you?", "I'm good"]
├── Thread "xyz-2" → ["Tell me a joke", "Why did..."]
└── Thread "pqr-3" → ["What's Python?", "Python is a..."]
```

### User Actions

**Action 1: Click "Thread abc-1"**
```
retrieve_all_threads()
    ↓
Returns: ['abc-1', 'xyz-2', 'pqr-3']
    ↓
Display in sidebar
```

**Action 2: Click on "How are you?" thread**
```
load_conversation('abc-1')
    ↓
Get state: {'messages': [HumanMessage('Hi'), AIMessage('Hello!'),...]}
    ↓
Convert to display format
    ↓
Show in chat window
```

**Action 3: User types "I'm doing great!"**
```
chatbot.invoke(
    {'messages': [HumanMessage("I'm doing great!")]},
    config={'configurable': {'thread_id': 'abc-1'}}
)
    ↓
Database loads previous state (previous 4 messages)
    ↓
LLM sees full context
    ↓
Returns response
    ↓
Add to message_history
    ↓
Database saves new checkpoint (5 messages now)
```

**Action 4: Click delete (🗑️) button**
```
Remove 'abc-1' from chat_threads list
    ↓
st.rerun()
    ↓
Remove from display
    ↓
(Note: Database thread still exists, can be recovered)
```

---

## 🗄️ Database Schema

### Auto-created by SqliteSaver:

```sql
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL PRIMARY KEY,
    checkpoint_ns TEXT DEFAULT '',
    created_at REAL,
    channel TEXT,
    version_num INTEGER DEFAULT 0,
    values TEXT,  -- JSON serialized state
    metadata TEXT
);
```

### Query Examples:

```sql
-- Get all threads
SELECT DISTINCT thread_id FROM checkpoints;

-- Get latest state for a thread
SELECT * FROM checkpoints 
WHERE thread_id = 'abc-1' 
ORDER BY created_at DESC 
LIMIT 1;

-- Get all states for a thread (history)
SELECT * FROM checkpoints 
WHERE thread_id = 'abc-1' 
ORDER BY created_at ASC;
```

---

## 💡 Key Features

### 1. **Multi-Conversation Support**
- Each thread = separate conversation
- Switch between conversations instantly
- Full history preserved

### 2. **Persistent Storage**
- Data survives app restart
- SQLite handles concurrent access
- Efficient queries

### 3. **User-Friendly UI**
- Sidebar navigation
- Rename conversations
- Delete conversations
- Auto-title from first message

### 4. **Thread Isolation**
- No cross-conversation contamination
- Each thread has own state
- LLM sees only relevant history

---

## 🚀 Advanced Operations

### Retrieve All Conversation Summaries
```python
def get_all_conversations():
    threads = retrieve_all_threads()
    conversations = []
    
    for thread_id in threads:
        messages = load_conversation(thread_id)
        
        title = "New Chat"
        first_message = ""
        last_update = None
        msg_count = len(messages)
        
        if messages:
            first_msg = next((m for m in messages if isinstance(m, HumanMessage)), None)
            if first_msg:
                first_message = first_msg.content[:50]
            last_update = "Just now"  # Can parse timestamps
        
        conversations.append({
            'thread_id': thread_id,
            'title': title,
            'first_message': first_message,
            'message_count': msg_count,
            'last_update': last_update
        })
    
    return conversations

# Display
for conv in get_all_conversations():
    print(f"[{conv['message_count']} messages] {conv['title']}")
    print(f"  First: {conv['first_message']}")
```

### Export Conversation to File
```python
import json

def export_conversation(thread_id, filename):
    messages = load_conversation(thread_id)
    
    export_data = {
        'thread_id': thread_id,
        'messages': [
            {
                'role': 'user' if isinstance(msg, HumanMessage) else 'assistant',
                'content': msg.content,
                'timestamp': ...
            }
            for msg in messages
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
```

### Search Conversations
```python
def search_conversations(query):
    threads = retrieve_all_threads()
    results = []
    
    for thread_id in threads:
        messages = load_conversation(thread_id)
        for msg in messages:
            if query.lower() in msg.content.lower():
                results.append({
                    'thread_id': thread_id,
                    'message': msg.content,
                    'role': type(msg).__name__
                })
    
    return results

# Usage
results = search_conversations("Python")
```

---

## 📊 Architecture Diagram

```
┌────────────────────────────────────────┐
│      Streamlit Frontend                │
│  ┌──────────────────────────────────┐  │
│  │ Sidebar: Thread List & Buttons   │  │
│  │ - ➕ New Chat                    │  │
│  │ - Thread 1 (✏️ 🗑️)              │  │
│  │ - Thread 2 (✏️ 🗑️)              │  │
│  │ - Thread 3 (✏️ 🗑️)              │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │ Main Chat Area                   │  │
│  │ - Display message history        │  │
│  │ - Get user input                 │  │
│  │ - Show AI responses              │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
                    ↓
         ┌──────────────────────┐
         │  LangGraph Backend   │
         │  - StateGraph        │
         │  - chat_node         │
         │  - SqliteSaver       │
         └──────────────────────┘
                    ↓
         ┌──────────────────────┐
         │   SQLite Database    │
         │   chatbot.db         │
         │  ┌────────────────┐  │
         │  │ checkpoints    │  │
         │  │ (all threads)  │  │
         │  └────────────────┘  │
         └──────────────────────┘
```

---

## 🔑 Files Included

| File | Purpose |
|------|---------|
| `backend.py` | LangGraph + SQLite setup |
| `streamlit_frontend_withdb.py` | Basic UI with DB |
| `stramlit_frontend_withdb_updated.py` | Enhanced UI (typo in name) |

---

## ✅ Production Checklist

- ✓ Database persistence
- ✓ Multi-conversation support
- ✓ Thread isolation
- ✓ Error handling
- ✓ User-friendly UI
- ✓ Message history display
- ✓ Rename conversations
- ✓ Delete conversations
- ⚠️ Add: User authentication
- ⚠️ Add: Rate limiting
- ⚠️ Add: Conversation search
- ⚠️ Add: Data export
- ⚠️ Add: Backup/restore

---

## 🏃 How to Run

```bash
# Install dependencies
pip install streamlit langgraph langchain-core

# Run application
streamlit run stramlit_frontend_withdb_updated.py
```

App opens at: `http://localhost:8501`

A `chatbot.db` file will be created automatically.

---

## 💾 Backup & Restore

```python
import shutil
from datetime import datetime

# Backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"chatbot_backup_{timestamp}.db"
shutil.copy('chatbot.db', backup_file)

# Restore
shutil.copy('chatbot_backup_20240101_120000.db', 'chatbot.db')
```

---

## ✅ What You've Learned

- ✓ SQLite database setup
- ✓ SqliteSaver checkpointer
- ✓ Multi-conversation architecture
- ✓ Thread management
- ✓ Conversation persistence
- ✓ Advanced Streamlit UI
- ✓ Thread retrieval and history
- ✓ Production-ready patterns

---

## 🔗 Complete Learning Path

1. **Folder 1 (Intro)**: Basic single-node chatbot
2. **Folder 2 (Persistence)**: Multi-node workflows & checkpointing
3. **Folder 3 (Basic UI)**: Streamlit frontend integration
4. **Folder 4 (Database)**: ← **You are here**
   - Production-ready with SQLite
   - Multi-conversation management
   - Persistent storage
   - Advanced UI features

---

## 🎓 Concepts Summary

| Concept | Where Used | Purpose |
|---------|-----------|---------|
| StateGraph | All folders | Define workflow |
| Checkpointer | Folders 1-4 | Save state |
| Threads | Folders 1-4 | Session management |
| SqliteSaver | Folder 4 | Persistent storage |
| Streamlit | Folders 3-4 | Build UI |
| Session State | Folders 3-4 | Frontend persistence |

---
