# backend/agents/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence
import operator

from agents.router import router
from agents.query_agent import create_query_agent
from agents.action_agent import create_action_agent
from tools import make_all_tools
from zoho.client import ZohoClient
from memory.short_term import short_term_memory


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    requires_confirmation: bool
    pending_action: dict


def build_graph(zoho_client: ZohoClient):
    all_tools = make_all_tools(zoho_client)

    query_tools = [
        all_tools["list_projects"],
        all_tools["list_tasks"],
        all_tools["get_task_details"],
        all_tools["list_project_members"],
        all_tools["get_task_utilisation"],
    ]

    action_tools = [
        all_tools["create_task"],
        all_tools["update_task"],
        all_tools["delete_task"],
    ]

    query_agent = create_query_agent(query_tools)
    action_agent = create_action_agent(action_tools)

    def router_node(state: AgentState) -> AgentState:
        decision = router.route(state)
        return {**state, "current_agent": decision}

    async def query_node(state: AgentState) -> AgentState:
        result = await query_agent.ainvoke(state)
        return {**state, "messages": result["messages"]}

    async def action_node(state: AgentState) -> AgentState:
        result = await action_agent.ainvoke(state)
        return {**state, "messages": result["messages"]}

    def route_decision(state: AgentState) -> str:
        return state.get("current_agent", "query_agent")

    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("query_agent", query_node)
    graph.add_node("action_agent", action_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "query_agent": "query_agent",
            "action_agent": "action_agent"
        }
    )

    graph.add_edge("query_agent", END)
    graph.add_edge("action_agent", END)

    return graph.compile(checkpointer=short_term_memory)