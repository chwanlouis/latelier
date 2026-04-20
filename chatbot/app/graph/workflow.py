"""LangGraph workflow definition."""
from langgraph.graph import END, StateGraph

from app.graph.nodes import generate_response, retrieve_context
from app.graph.state import GraphState


def build_workflow():
    builder = StateGraph(GraphState)

    builder.add_node("retrieve_context", retrieve_context)
    builder.add_node("generate_response", generate_response)

    builder.set_entry_point("retrieve_context")
    builder.add_edge("retrieve_context", "generate_response")
    builder.add_edge("generate_response", END)

    return builder.compile()


workflow = build_workflow()
