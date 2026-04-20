"""LangGraph node implementations."""
import json
import re

from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.graph.state import GraphState
from app.mcp_client import client as mcp

settings = get_settings()
_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)

_SYSTEM_PROMPT = """You are a culinary AI assistant specialising in molecular food science.
You help chefs and menu developers discover optimal food pairings based on shared flavour molecules.
You are aware of the OR6A2 gene mutation (10-20% prevalence, predominantly East Asian populations)
which causes certain aldehydes in cilantro to taste soapy.

Use the provided context (ingredients, molecules, pairing scores) to give evidence-based recommendations.
Always flag dishes that may be affected by OR6A2 when relevant."""


async def retrieve_context(state: GraphState) -> GraphState:
    """Fetch relevant data from the MCP server based on the latest user message."""
    last_user_msg = state["messages"][-1].content
    context: dict = {}

    # Extract ingredient names mentioned in message (naive extraction)
    words = re.findall(r"\b[A-Za-z]{3,}\b", last_user_msg)
    candidates = [w.lower() for w in words if w.lower() not in _STOP_WORDS]

    if len(candidates) >= 2:
        try:
            score = await mcp.pairing_score(candidates[0], candidates[1])
            context["pairing_score"] = score
        except Exception:
            pass

    if candidates:
        try:
            gf = await mcp.genetic_filter(candidates[0])
            context["genetic_filter"] = gf
        except Exception:
            pass

    return {**state, "context": context}


async def generate_response(state: GraphState) -> GraphState:
    """Call the LLM with messages + context."""
    context_str = json.dumps(state.get("context", {}), indent=2)
    system = SystemMessage(
        content=f"{_SYSTEM_PROMPT}\n\nRelevant data from knowledge base:\n{context_str}"
    )
    response = await _llm.ainvoke([system, *state["messages"]])
    return {**state, "messages": [AIMessage(content=response.content)]}


_STOP_WORDS = {
    "the", "and", "are", "for", "with", "this", "that", "from", "they",
    "have", "has", "what", "which", "who", "where", "when", "how", "can",
    "you", "your", "our", "any", "all", "more", "does", "about", "pair",
    "pairs", "pairing", "food", "ingredient", "ingredients", "taste", "flavor",
}
