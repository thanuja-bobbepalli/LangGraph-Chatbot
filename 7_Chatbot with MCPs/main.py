# arith_server.py

from __future__ import annotations
from fastmcp import FastMCP

mcp=FastMCP("arith")

def _as_number(x):
    if isinstance(x,(int,float)):
        return float(x)
    if isinstance(x,str):
        return float(x.strip())
    raise TypeError("Expected a num (int\float or numeric string)")

@mcp.tool()
async def add(a:float ,b: float)->float:
    """Use this tool to perform addition of two numbers.
Always use this tool for any addition instead of calculating yourself."""
    return _as_number(a)+_as_number(b)

@mcp.tool()
async def subtract(a:float ,b: float)->float:
    """Use this tool to perform subtraction of two numbers.
Always use this tool for any addition instead of calculating yourself."""
    return _as_number(a) - _as_number(b) 

@mcp.tool()
async def multiply(a:float ,b: float)->float:
    """Use this tool to perform multiplication of two numbers.
Always use this tool for any addition instead of calculating yourself."""
    result=_as_number(a) * _as_number(b)
    return result

@mcp.tool()
async def devide(a:float ,b: float)->float:
    """Use this tool to perform di of two numbers.
Always use this tool for any addition instead of calculating yourself."""
    a=_as_number(a)
    b=_as_number(b)
    if b==0:
        raise ZeroDivisionError("Division by zero ")
    result=a/b
    return result

@mcp.tool()
async def power(a:float ,b: float)->float:
    """Use this tool to perform power of two numbers.
Always use this tool for any addition instead of calculating yourself."""
    result=_as_number(a) ** _as_number(b)
    return result

