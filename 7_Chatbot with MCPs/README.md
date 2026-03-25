# MCP (Model Context Protocol) with LangGraph — README

## 1. What is MCP and why it matters

MCP (Model Context Protocol) is a standard that allows language models to interact with tools in a structured way.

In traditional systems, tools are directly written inside the code. This makes the system hard to scale and maintain. MCP solves this by separating tools from the model.

Key idea:
The model uses tools, but tools are not tightly connected to the model code.

---

## 2. Example: Multiple tools and GitHub integration

Common tools:

* Search tool
* Calculator tool
* Stock price tool
* GitHub tool (issues, repos, commits)

Without MCP:
All tools are defined inside the same codebase.

Example:

```python
tools = [search_tool, calculator, stock_tool]
llm.bind_tools(tools)
```

With MCP:

* Tools run as separate servers
* The model connects to them when needed

Example flow:
User asks: “Calculate profit for AAPL”

Steps:

1. Model fetches stock price using stock tool
2. Model uses calculator tool
3. Final answer is generated

---

## 3. Problem with traditional tool-based systems

Main issues:

1. Tight coupling
   Tools are directly connected to the code

2. API changes break system
   Example:

```python
# Old
get_price(symbol="AAPL")

# New
get_price(ticker="AAPL")
```

3. Hard to maintain
   Updating one tool may require changing multiple parts of the system

Conclusion:
Traditional tool systems are brittle and not scalable

---

## 4. MCP solution: Separation of concerns

MCP separates responsibilities:

* Client (LangGraph): decides when to use tools
* Server: provides tools
* Protocol: defines communication

Benefits:

* Tools can be updated independently
* Easy to add or remove tools
* Clean and modular architecture

Key idea:
The client does not need to know how the tool is implemented, only how to call it.

---

## 5. Why sync to async conversion is required

MCP libraries are asynchronous.
1. Synchronous Code (Sync)
In synchronous programming, code is executed sequentially, line-by-line, in the order it is written. 
**Blocking**: Each operation must complete before the next one starts. If a task takes a long time (e.g., loading a large file, calling a slow database), the entire program halts ("blocks") until that task is done.

2. Asynchronous Code (Async)
Asynchronous code allows the program to start a long-running task and move on to the next task immediately, without waiting for the first one to finish. 

**Non-Blocking**: When a slow task (e.g., a network request) is initiated, it runs in the background. The main execution thread continues, allowing the UI to remain responsive.
Synchronous code:

```python
result = tool()
```

Asynchronous code:

```python
result = await tool()
```

Why async is needed:

* Handles multiple tool calls efficiently
* Non-blocking execution
* Better performance

---

## 6. Async programming basics

1. async
   Defines an asynchronous function

```python
async def fetch_data():
    return "data"
```

2. await
   Waits for the result of an async function

```python
result = await fetch_data()
```

3. Event loop
   Executes async tasks

Simple idea:
Sync = one task at a time
Async = multiple tasks without blocking

---

## 7. Building an MCP client in LangGraph

Goal: connect LangGraph to an MCP server

Steps:

1. Connect to server

```python
client = MCPClient(server_url)
```

2. Get tools

```python
tools = await client.list_tools()
```

3. Bind tools to model

```python
llm_with_tools = llm.bind_tools(tools)
```

Example:
User asks: “Multiply 10 and 20”

Flow:

* Model detects math operation
* Calls math tool from MCP server
* Gets result
* Returns answer

---

## 8. Adding a remote MCP server (expense tracker)

You can connect to external servers that provide tools.

Example:

```python
client = MCPClient("https://expense-server.com")
tools = await client.list_tools()
```

Available tools:

* add_expense
* get_expenses
* analyze_spending

User query:
“Show my total expenses this month”

Flow:

* Model calls get_expenses
* Server returns data
* Model formats response

Important point:
You did not implement the tool, you only connected to it.

---

## 9. Overall architecture

User
↓
LangGraph (LLM client)
↓
MCP protocol
↓
MCP server (tools)
↓
External APIs or systems

---

## 10. Key takeaways

* MCP standardizes tool interaction
* Removes tight coupling between model and tools
* Makes systems scalable and modular
* Requires async programming
* Supports both local and remote tools
* Works well with LangGraph

---

## Final summary

MCP allows language models to use tools in a structured and scalable way. It solves the limitations of traditional tool-based systems by separating tool implementation from model logic. With async support and server-based tools, MCP enables building flexible and maintainable AI systems that can easily integrate real-world functionalities.
