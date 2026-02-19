from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from database.session import get_session
from auth.auth_handler import get_current_user
from agents.chat_agent import ChatAgent, AgentRequest
from sqlmodel import Session

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/chat")
async def process_agent_request(request: AgentRequest):
    """
    Process a natural language request through the AI agent.

    Args:
        request: Contains user message, user ID, and conversation history

    Returns:
        Response from the AI agent with tool calls and results
    """
    try:
        agent = ChatAgent()
        response = await agent.process_request(request)

        return {
            "response_text": response.response_text,
            "tool_calls": response.tool_calls,
            "success": response.success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agent request: {str(e)}")


@router.post("/chat-secured")
async def process_secured_agent_request(
    request: AgentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process a natural language request through the AI agent with authentication.

    Args:
        request: Contains user message, user ID, and conversation history
        current_user: Authenticated user data
        session: Database session

    Returns:
        Response from the AI agent with tool calls and results
    """
    # Ensure the request is for the authenticated user
    if request.user_id != str(current_user.get("id")):
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Cannot access another user's tasks"
        )

    try:
        agent = ChatAgent()
        response = await agent.process_request(request)

        return {
            "response_text": response.response_text,
            "tool_calls": response.tool_calls,
            "success": response.success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing agent request: {str(e)}")