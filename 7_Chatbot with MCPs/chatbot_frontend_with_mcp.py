import streamlit as st
from chatbot_backend_with_mcp import chatbot, retrieve_all_threads, submit_async_task
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

import uuid
import queue

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
load_dotenv()

# ------------------ LLM (for title generation) ------------------
llm = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",  
    task="text-generation",
    temperature=0.2, 
    max_new_tokens=20 
)
llm = ChatHuggingFace(llm=llm)

# ------------------ Utility functions ------------------

def generate_thread_id():
    return uuid.uuid4()

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

# ------------------ Session setup ------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    chat_threads = []

    for t in retrieve_all_threads():
        messages = chatbot.get_state(
            config={"configurable": {"thread_id": t}}
        ).values.get("messages", [])

        title = "New Chat"
        for msg in messages:
            if isinstance(msg, HumanMessage):
                title = msg.content[:30]
                break

        chat_threads.append({
            "id": t,
            "title": title
        })

    st.session_state['chat_threads'] = chat_threads

add_thread(st.session_state['thread_id'])

# ------------------ Sidebar ------------------

st.sidebar.title('LangGraph MCP Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread in st.session_state['chat_threads'][::-1]:

    col1, col2, col3 = st.sidebar.columns([3, 1, 1])

    # Select thread
    if col1.button(thread["title"], key=f"thread_{thread['id']}", use_container_width=True):
        st.session_state['thread_id'] = thread["id"]

        messages = load_conversation(thread["id"])
        temp_messages = []

        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

    # Rename
    if col2.button("✏️", key=f"rename_btn_{thread['id']}"):
        st.session_state[f"rename_mode_{thread['id']}"] = True

    if st.session_state.get(f"rename_mode_{thread['id']}", False):
        new_title = st.sidebar.text_input(
            "Rename:",
            value=thread["title"],
            key=f"rename_input_{thread['id']}"
        )

        if st.sidebar.button("Save", key=f"save_{thread['id']}"):
            thread["title"] = new_title
            st.session_state[f"rename_mode_{thread['id']}"] = False
            st.rerun()

    # Delete
    if col3.button("🗑️", key=f"delete_{thread['id']}"):
        st.session_state['chat_threads'] = [
            t for t in st.session_state['chat_threads']
            if t["id"] != thread["id"]
        ]

        if st.session_state['thread_id'] == thread["id"]:
            reset_chat()

        st.rerun()

# ------------------ Main UI ------------------

# Render history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # Auto title generation
    for thread in st.session_state['chat_threads']:
        if thread["id"] == st.session_state["thread_id"] and thread["title"] == "New Chat":
            try:
                title_prompt = f"""Generate a short chat title.

STRICT RULES:
- Maximum 5 words
- No punctuation
- No explanation
- No full sentence
- Only return the title

User message:
{user_input}
"""
                raw_title = llm.invoke(title_prompt).content
                title = raw_title.strip().replace('"', '').replace("'", "")
                title = title.split("\n")[0]
                title = " ".join(title.split()[:5])
                thread["title"] = title
            except:
                pass

    # Show user message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn",
    }

    # ------------------ Assistant ------------------
    with st.chat_message("assistant"):

        status_holder = {"box": None}

        def ai_only_stream():
            event_queue: queue.Queue = queue.Queue()

            async def run_stream():
                try:
                    async for message_chunk, metadata in chatbot.astream(
                        {"messages": [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode="messages",
                    ):
                        event_queue.put((message_chunk, metadata))
                except Exception as e:
                    event_queue.put(("error", e))
                finally:
                    event_queue.put(None)

            submit_async_task(run_stream())

            while True:
                item = event_queue.get()
                if item is None:
                    break

                message_chunk, metadata = item

                if message_chunk == "error":
                    raise metadata

                # Tool UI
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")

                    print("TOOL CALLED:", tool_name)
                    
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream AI tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished",
                state="complete",
                expanded=False
            )

    # Save response
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )