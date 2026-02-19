from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from sqlmodel import Session
from database.session import get_session
from auth.auth_handler import get_current_user
from models.conversation import Conversation, ConversationCreate
from models.message import Message, MessageCreate, SenderType
from database.crud import (
    create_conversation,
    get_conversation_by_id,
    get_messages_by_conversation_id,
    create_message,
    get_conversations_by_user_id
)
from agents.chat_agent import ChatAgent, AgentRequest
from pydantic import BaseModel
from pydantic import field_validator
import uuid

router = APIRouter(prefix="/api/{user_id}", tags=["chat"])

# Request/Response models for chat endpoints
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 10000:  # Limit message length
            raise ValueError('Message too long, maximum 10000 characters')
        return v.strip()


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: List[Dict[str, Any]]


@router.post("/chat")
async def process_chat_message(
    user_id: str,
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process user message and return AI response

    Args:
        user_id: User ID from path parameter (validated against JWT token)
        request: Contains user message and optional conversation ID
        current_user: Authenticated user data
        session: Database session

    Returns:
        ChatResponse with conversation ID, AI response, and any tool calls
    """
    # Validate that the user_id in the path matches the authenticated user
    if str(current_user.get("id")) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Cannot access another user's chat"
        )

    user_uuid = uuid.UUID(user_id)

    # If no conversation_id provided, create a new conversation
    conversation_id = None
    is_new_conversation = False
    if request.conversation_id:
        try:
            conversation_id = uuid.UUID(request.conversation_id)
            # Verify the conversation belongs to the user
            conversation = get_conversation_by_id(session, conversation_id, user_uuid)
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found or does not belong to user"
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid conversation ID format"
            )
    else:
        # Create a new conversation with a placeholder title
        conversation_title = f"Chat: {request.message[:50]}..." if len(request.message) > 50 else f"Chat: {request.message}"
        conversation_create = ConversationCreate(user_id=user_uuid, title=conversation_title)
        conversation = create_conversation(session, conversation_create)
        conversation_id = conversation.conversation_id
        is_new_conversation = True

    # Get existing messages for conversation history
    existing_messages = get_messages_by_conversation_id(session, conversation_id)
    conversation_history = []
    for msg in existing_messages:
        conversation_history.append({
            "role": "user" if msg.sender_type == SenderType.user else "assistant",
            "content": msg.content
        })

    # Create and save user message
    user_message = MessageCreate(
        conversation_id=conversation_id,
        sender_type=SenderType.user,
        content=request.message
    )
    saved_user_message = create_message(session, user_message)

    # Prepare agent request with conversation history
    agent_request = AgentRequest(
        user_message=request.message,
        user_id=user_id,
        conversation_history=conversation_history
    )

    # Process through AI agent
    try:
        agent = ChatAgent()
        response = await agent.process_request(agent_request)

        # Create and save agent response message
        agent_message = MessageCreate(
            conversation_id=conversation_id,
            sender_type=SenderType.agent,
            content=response.response_text
        )
        create_message(session, agent_message)

        # If this is a new conversation and we have an agent response, consider updating the conversation title
        # based on the content of the conversation for better identification
        if is_new_conversation and response.response_text and len(existing_messages) == 0:
            # Create a more descriptive title based on the initial exchange
            title_content = request.message[:30] if len(request.message) > 30 else request.message
            updated_title = f"{title_content}..."
            from database.crud import update_conversation
            update_conversation(session, conversation_id, user_uuid, title=updated_title)

        # Return response
        return ChatResponse(
            conversation_id=str(conversation_id),
            response=response.response_text,
            tool_calls=response.tool_calls
        )
    except Exception as e:
        # If agent processing fails, still save the user message but return error
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/conversations")
def get_user_conversations(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve user's conversation history

    Args:
        user_id: User ID from path parameter (validated against JWT token)
        current_user: Authenticated user data
        session: Database session

    Returns:
        List of conversation summaries
    """
    # Validate that the user_id in the path matches the authenticated user
    if str(current_user.get("id")) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Cannot access another user's conversations"
        )

    user_uuid = uuid.UUID(user_id)
    conversations = get_conversations_by_user_id(session, user_uuid)

    return [
        {
            "conversation_id": str(conv.conversation_id),
            "title": conv.title or f"Conversation {conv.created_at.strftime('%Y-%m-%d %H:%M')}",
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation_history(
    user_id: str,
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Retrieve specific conversation history

    Args:
        user_id: User ID from path parameter (validated against JWT token)
        conversation_id: Conversation ID to retrieve
        current_user: Authenticated user data
        session: Database session

    Returns:
        Array of messages in chronological order
    """
    # Validate that the user_id in the path matches the authenticated user
    if str(current_user.get("id")) != user_id:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Cannot access another user's conversations"
        )

    try:
        user_uuid = uuid.UUID(user_id)
        conv_uuid = uuid.UUID(conversation_id)

        # Verify the conversation belongs to the user
        conversation = get_conversation_by_id(session, conv_uuid, user_uuid)
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or does not belong to user"
            )

        messages = get_messages_by_conversation_id(session, conv_uuid)

        return [
            {
                "message_id": str(msg.message_id),
                "sender_type": msg.sender_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "status": msg.status.value
            }
            for msg in messages
        ]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID format"
        )