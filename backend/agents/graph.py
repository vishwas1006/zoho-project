# backend/agents/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

def build_graph(query_agent, action_agent, router):
    graph = StateGraph(...)
    graph.add_node("router", router)
    graph.add_node("query_agent", query_agent)
    graph.add_node("action_agent", action_agent)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_decision)
    graph.add_edge("query_agent", END)
    graph.add_edge("action_agent", END)

    return graph.compile(checkpointer=MemorySaver())