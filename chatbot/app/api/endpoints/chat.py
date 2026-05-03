from fastapi import APIRouter

from app.graph.workflow import workflow
from app.graph.state import GraphState
from app.models.chat import ChatRequest, ChatResponse
from app.services.session_service import (
    append_message,
    delete_session,
    get_history,
    get_preferences,
    new_session,
    set_preferences,
)
from langchain_core.messages import AIMessage, HumanMessage

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or new_session()

    history = get_history(session_id)
    saved_prefs = get_preferences(session_id)
    user_msg = HumanMessage(content=request.message)
    append_message(session_id, user_msg)

    state: GraphState = {
        "messages": history + [user_msg],
        "session_id": session_id,
        "context": {},
        "preferences": saved_prefs,
    }

    result = await workflow.ainvoke(state)
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    reply = ai_messages[-1].content if ai_messages else "I could not generate a response."

    append_message(session_id, AIMessage(content=reply))
    # Persist updated preferences for the next turn
    set_preferences(session_id, result.get("preferences") or [])

    return ChatResponse(session_id=session_id, reply=reply)


@router.delete("/{session_id}")
async def clear_session(session_id: str):
    delete_session(session_id)
    return {"message": "Session cleared"}
