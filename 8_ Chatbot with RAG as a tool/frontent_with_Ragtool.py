import streamlit as st
import uuid

from backend_rag_tool import (
    chatbot,
    ingest_pdf,
    retrieve_all_threads,
    thread_document_metadata,
)
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from dotenv import load_dotenv
load_dotenv()


llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
)
llm= ChatHuggingFace(llm=llm)

#-----------------------------------------------------
#                  Utility functions
#-------------------------------------------------

def generate_thread_id():
    thread_id= uuid.uuid4()
    return thread_id


def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    
    add_thread(thread_id,"New Chat") #default chat 
    st.session_state['message_history']=[]
    
    
def add_thread(thread_id,title="New Chat"):
    if not any( t["id"]==thread_id for t in st.session_state['chat_threads']):
        st.session_state['chat_threads'].append({
            "id":thread_id,
            "title":title})
        
def load_conversation(thread_id):
    state=chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    return state.values.get('messages',[])

#------------------------------------------------------------------------
# Session setup 
# ------------------------------------------------------------------------

if 'message_history' not in st.session_state:
    st.session_state['message_history']=[]
    
if 'thread_id' not in st.session_state:
  st.session_state['thread_id']= generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    threads = retrieve_all_threads()
    chat_threads = []

    for t in retrieve_all_threads():
        messages = chatbot.get_state(
        config={"configurable": {"thread_id": t}}
        ).values.get("messages", [])

    # Try to get first user message
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

if "ingested_docs" not in st.session_state:
    st.session_state["ingested_docs"] = {}
   
add_thread(st.session_state['thread_id'])

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})
threads = st.session_state["chat_threads"][::-1]
selected_thread = None
#------------------------------------------------------------------
#                                Sidebar UI 
# -----------------------------------------------------------------

st.sidebar.title("LangGraph Chatbot with PDF")

thread_key = str(st.session_state["thread_id"])
thread_docs = st.session_state["ingested_docs"].setdefault(thread_key, {})

# -------- New Chat --------
if st.sidebar.button("New Chat", use_container_width=True):
    reset_chat()
    st.rerun()

# -------- PDF STATUS --------
if thread_docs:
    latest_doc = list(thread_docs.values())[-1]
    st.sidebar.success(
        f"Using `{latest_doc.get('filename')}` "
        f"({latest_doc.get('chunks')} chunks)"
    )
else:
    st.sidebar.info("No PDF uploaded")

# -------- PDF UPLOAD --------
uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_pdf:
    if uploaded_pdf.name in thread_docs:
        st.sidebar.info(f"{uploaded_pdf.name} already added")
    else:
        with st.sidebar.status("Indexing PDF...", expanded=True):
            summary = ingest_pdf(
                uploaded_pdf.getvalue(),
                thread_id=thread_key,
                filename=uploaded_pdf.name,
            )
            thread_docs[uploaded_pdf.name] = summary
            
for thread in st.session_state['chat_threads'][::-1]:

    col1, col2, col3 = st.sidebar.columns([3, 1, 1])

    # Chat Title
    if col1.button(thread["title"], key=f"thread_{thread['id']}", use_container_width=True):
        st.session_state['thread_id'] = thread["id"]
        thread_key = str(st.session_state["thread_id"])
        st.session_state["ingested_docs"].setdefault(thread_key, {})
        messages = load_conversation(thread["id"])

        temp_messages = []
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages

    # ✏️ Rename
    if col2.button("✏️", key=f"rename_btn_{thread['id']}", use_container_width=True):
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

    # 🗑️ Delete
    if col3.button("🗑️", key=f"delete_{thread['id']}", use_container_width=True):
        st.session_state['chat_threads'] = [
            t for t in st.session_state['chat_threads']
            if t["id"] != thread["id"]
        ]

        if st.session_state['thread_id'] == thread["id"]:
            reset_chat()

        st.rerun()
        
# ------------------------------------------------------------------
#                              Main UI 
# -----------------------------------------------------------------
st.title("Multi Utility Chatbot")
# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
user_input = st.chat_input('Ask about your document or use tools')

if user_input:
    
    #If firast message-> update title
    for thread in st.session_state['chat_threads']:
        if thread["id"]==st.session_state["thread_id"] and thread["title"]=="New Chat":
            title_prompt = f""" Generate a short title for the following user message.

STRICT RULES:
- Output ONLY the title
- Maximum 5 words
- No punctuation
- No full sentences
- No explanations
- No quotes
- No extra text
- Do NOT include words like "Title:" or "Answer:"
- compress the all information and got to now what message user ask and whats inside the chat and make a title . max words 4 .
User message:
{user_input}"""
            raw_title = llm.invoke(title_prompt).content

            # Clean aggressively
            title = raw_title.strip()
            title = title.replace('"', '').replace("'", "")
            title = title.split("\n")[0]
            title = " ".join(title.split()[:5])
            thread["title"] = title

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    thread_key = str(st.session_state["thread_id"])
    CONFIG = {
        "configurable": {"thread_id": thread_key},
        "metadata": {"thread_id": thread_key},
        "run_name": "chat_turn",
    }
     # first add the message to message_history
    # Assistant streaming block
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, _ in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
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

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    doc_meta = thread_document_metadata(thread_key)
    if doc_meta:
        st.caption(
            f"Document indexed: {doc_meta.get('filename')} "
            f"(chunks: {doc_meta.get('chunks')}, pages: {doc_meta.get('documents')})"
        )

st.divider()

if selected_thread:
    st.session_state["thread_id"] = selected_thread
    messages = load_conversation(selected_thread)

    temp_messages = []
    for msg in messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        temp_messages.append({"role": role, "content": msg.content})
    st.session_state["message_history"] = temp_messages
    st.session_state["ingested_docs"].setdefault(str(selected_thread), {})
    st.rerun()

     