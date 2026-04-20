"""LangGraph conversation state definition."""
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator


class GraphState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    session_id: str
    context: dict  # additional data fetched from MCP / Neo4j
