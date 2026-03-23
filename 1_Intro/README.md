# LangGraph Basic Chatbot - Intro Guide

## Overview
This folder demonstrates the **fundamental concepts of LangGraph**, a framework for building stateful AI applications using graph-based workflows. You'll learn how to create a simple chatbot with conversation memory.

---

## 📚 Core Concepts

### 1. **StateGraph - The Foundation**
A `StateGraph` is the core building block in LangGraph. It's a directed graph where:
- **Nodes** = Functions that process data
- **Edges** = Control flow between nodes
- **State** = Shared data passed between nodes

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')    # Entry point
graph.add_edge('chat_node', END)      # Exit point
```

### 2. **State Management with TypedDict**
State is the "memory" of your application. Use `TypedDict` to define what data flows through your graph:

```python
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # messages: A list of conversation messages
    # Annotated[...]: Metadata about how to merge messages
    # add_messages: Reducer function that appends new messages
```

**Why `Annotated`?**
- Tells LangGraph how to merge messages when multiple nodes update state
- `add_messages` automatically appends new messages to the list

### 3. **Nodes - Processing Functions**
Nodes are functions that take state as input and return state updates:

```python
def chat_node(state: ChatState):
    messages = state['messages']           # Get conversation history
    response = llm.invoke(messages)        # Get LLM response
    return {'messages': [response]}        # Return updated state
```

### 4. **LLM Integration**
The Large Language Model (LLM) is the "brain" of your chatbot:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()  # Load API keys from .env file
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
```

### 5. **Memory Management with Checkpointers**
Checkpointers save the state at each step, enabling:
- **Conversation memory** across multiple turns
- **Thread management** (multiple conversations)
- **State retrieval** (replay conversations)

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)
```

---

## 🔧 How It Works (Step-by-Step)

### Step 1: Build the Graph
```python
graph = StateGraph(ChatState)
graph.add_node('chat_node', chat_node)
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)
```
Creates a simple linear flow: START → chat_node → END

### Step 2: Compile with Checkpointer
```python
chatbot = graph.compile(checkpointer=MemorySaver())
```
Converts the graph definition into an executable workflow with memory support.

### Step 3: Invoke the Chatbot
```python
config = {'configurable': {'thread_id': 'user-1'}}
initial_state = {'messages': [HumanMessage(content="Hello")]}
response = chatbot.invoke(initial_state, config=config)
```
- `thread_id`: Unique identifier for this conversation
- `messages`: Starting conversation state
- Returns: Updated state with LLM response

---

## 📋 Example Usage

### Example 1: Single Turn Conversation
```python
from langchain_core.messages import HumanMessage

# Initial state
state = {
    'messages': [HumanMessage(content="What is the capital of India?")]
}

# Get response
result = chatbot.invoke(state, config={'configurable': {'thread_id': 'user-1'}})
print(result['messages'][-1].content)
# Output: "The capital of India is **New Delhi**."
```

### Example 2: Multi-Turn Conversation (Using Memory)
```python
config = {'configurable': {'thread_id': 'user-1'}}

# Turn 1
response1 = chatbot.invoke(
    {'messages': [HumanMessage(content="What is AI?")]},
    config=config
)

# Turn 2 - Chatbot remembers previous context!
response2 = chatbot.invoke(
    {'messages': [HumanMessage(content="Give me an example")]},
    config=config
)
# The LLM sees BOTH messages + context from Thread 1
```

---

## 🎯 Key Workflow: How Messages Flow

```
User Input
    ↓
Initial State: {'messages': [HumanMessage(content="user query")]}
    ↓
START → chat_node (LLM processes all messages)
    ↓
LLM returns response as AIMessage
    ↓
Node returns: {'messages': [AIMessage(content="response")]}
    ↓
Reducer (add_messages) merges with existing messages
    ↓
Final State: {'messages': [HumanMessage(...), AIMessage(...), ...]}
    ↓
END → Checkpointer saves state to thread_id
```

---

## 🔑 Important Components Explained

| Component | Purpose |
|-----------|---------|
| **StateGraph** | Defines the workflow structure |
| **TypedDict** | Specifies what data flows through the graph |
| **add_messages** | Reducer that merges new messages into state |
| **Node** | Function that processes state |
| **Edge** | Connection between nodes (flow control) |
| **Checkpointer** | Saves/retrieves state snapshots |
| **thread_id** | Unique conversation identifier |
| **config** | Runtime configuration for the chatbot |

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────┐
│        ChatState (TypedDict)            │
│  - messages: List[BaseMessage]          │
└─────────────────────────────────────────┘
              ↑         ↓
              │         │
         (input)   (output)
              │         │
┌─────────────────────────────────────────┐
│          StateGraph                     │
│  START → chat_node(LLM) → END           │
└─────────────────────────────────────────┘
              ↓
    MemorySaver (Checkpointer)
              ↓
    Thread Storage {thread_id: state}
```

---

## 🚀 Next Steps

1. **Try modifying** the prompt to the LLM
2. **Add multiple turns** to test memory
3. **Experiment with different thread_ids** to see separate conversations
4. **Check folder `2_persistant`** for multi-node workflows
5. **Check `3_Basic UI`** for Streamlit integration

---

## 📝 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| LLM responses not using context | Ensure all previous messages are in state |
| Thread data not persisting | Use thread_id consistently |
| Memory growing too large | Implement message pruning or summarization |
| Multiple conversations mixing | Use separate thread_ids |

---

## ✅ What You've Learned

- ✓ How to define state with TypedDict
- ✓ How to create nodes and edges
- ✓ How to integrate LLMs into workflows
- ✓ How to save conversation memory with checkpointers
- ✓ How multi-turn conversations work
- ✓ Thread management basics
