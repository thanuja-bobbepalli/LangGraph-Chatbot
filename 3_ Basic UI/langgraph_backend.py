from langgraph.graph import StateGraph ,START ,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from langgraph.graph.message import add_messages
from dotenv import load_dotenv


# llm=ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite')
# model= ChatHuggingFace(llm=llm)

from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint

load_dotenv()
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V3.2",
    task="text-generation",
)
llm= ChatHuggingFace(llm=llm)
class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def chat_node(state:ChatState):
    messages = state['messages']
    response=llm.invoke(messages)
    return {"messages":[response]}

#checkppinter 
checkpointer =InMemorySaver()

graph=StateGraph(ChatState)
graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot= graph.compile(checkpointer=checkpointer)
