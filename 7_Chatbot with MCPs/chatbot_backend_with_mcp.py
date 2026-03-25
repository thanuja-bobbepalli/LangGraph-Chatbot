from langgraph.graph import StateGraph ,START ,END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode ,tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from langchain_core.messages import BaseMessage,HumanMessage,AIMessage
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool,BaseTool

from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import aiosqlite
import requests
import asyncio
import threading


# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever,daemon=True)
_ASYNC_THREAD.start()

def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro,_ASYNC_LOOP)

def run_async(coro):
    return _submit_async(coro).result()


def submit_async_task(coro):
    """Schedule a coroutine on the backend event loop."""
    return _submit_async(coro)


# **************************** Model ***************************
load_dotenv()
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
)
llm= ChatHuggingFace(llm=llm) 

#----------------------toolls-------------------------------------

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=JIENSG24LKB220MQ"
    r = requests.get(url)
    return r.json()

client =MultiServerMCPClient(
    {
        "arith":{
            "transport":"stdio",
            "command":"python3",
            "args":["/Users/Dell/Desktop/Tanuja/main.py"]
            # which is a server file contains tools  (which is located in the local system and also its copy available in current folder main.py)
            
        }
    }
)

def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception:
        return []

mcp_tools = load_mcp_tools()
tools = [search_tool, get_stock_price, *mcp_tools]
llm_with_tools = llm.bind_tools(tools) if tools else llm

#-------------------------------------------------------------------------
# 3. State
#--------------------------------------------------------------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

#-------------------------------------------------------------------------
# 4. Nodes 
#-----------------------------------------------------------------------
async def chat_node(state: ChatState):
    messages = state['messages']
    system_msg = AIMessage(content="""
You are a strict tool-using assistant.

RULES:
- Always use tools for math operations
- Never calculate on your own
- If numbers are involved, MUST call a tool
""")

    response = await llm_with_tools.ainvoke( [system_msg]+messages)
    return {"messages": [response]}

tool_node=ToolNode(tools) if tools else None

#---------------------------------------------------------------
# 5. checkpinter
#----------------------------------------------------------------
async def _init_checkpointer():
    conn =await aiosqlite.connect(database='chatbot.db')
    return AsyncSqliteSaver(conn)

checkpointer = run_async(_init_checkpointer())
#-----------------------------------------------------------------------
# 6. Graph 
#----------------------------------------------------------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools",tool_node)
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')
else :
    graph.add_edge("chat_node",END)
    
chatbot = graph.compile(checkpointer=checkpointer)

#--------------------------------------------------------------------------
# 7. Helper 
#---------------------------------------------------------------------------
async def _alist_threads():
    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
    
def retrieve_all_threads():
    return run_async(_alist_threads())

