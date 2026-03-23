import streamlit as st
from backend import chatbot,retrieve_all_threads
from langchain_core.messages import HumanMessage,AIMessage
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint

load_dotenv()
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V3.2",
    task="text-generation",
)
llm= ChatHuggingFace(llm=llm)
#**************Utility functions

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

#*********************** Session setup ****************

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

    
add_thread(st.session_state['thread_id'])

#********************88 Sidebar UI ******************************

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New chat'):
    reset_chat()
    
st.sidebar.header('My conversations')

for thread in st.session_state['chat_threads'][::-1]:

    col1, col2, col3 = st.sidebar.columns([3, 1, 1])

    # Chat Title
    if col1.button(thread["title"], key=f"thread_{thread['id']}", use_container_width=True):
        st.session_state['thread_id'] = thread["id"]

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
# **************************************** Main UI ************************************
# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        
user_input = st.chat_input('Type here')

if user_input:
    
    #If firast message-> update title
    for thread in st.session_state['chat_threads']:
        if thread["id"]==st.session_state["thread_id"] and thread["title"]=="New Chat":
            title_prompt = f""" Return ONLY the title.
No explanation.
No sentences.
No extra text.

Title (max 5 words):
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

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }
     # first add the message to message_history
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    
    

     