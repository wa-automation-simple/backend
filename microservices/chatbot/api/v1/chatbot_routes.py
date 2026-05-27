"""
Chatbot API Routes - v1
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from api.deps import get_db, verify_static_token, get_chatbot_by_token
from schemas.serializers import (
    ChatbotCreate, ChatbotUpdate, ChatbotResponse,
    ChatbotAgentCreate, ChatbotAgentResponse,
    ChatbotNodeCreate, ChatbotNodeResponse,
    ChatbotToolCreate, ChatbotToolResponse,
    ChatRequest, ChatResponse, ChatMessageResponse,
    ConversationResponse
)

router = APIRouter(prefix="/api/v1", tags=["chatbot"])


@router.post("/chatbots", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
def create_chatbot(chatbot_data: ChatbotCreate, db: Session = Depends(get_db)):
    """Create a new chatbot (JWT auth required - handled by gateway)"""
    from models.chatbot import Chatbot
    import secrets
    
    # Generate unique static token for this chatbot
    static_token = f"chat_{secrets.token_hex(32)}"
    
    db_chatbot = Chatbot(
        user_id=1,  # Should come from JWT token
        **chatbot_data.dict(),
        static_token=static_token
    )
    
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    
    return db_chatbot


@router.get("/chatbots", response_model=List[ChatbotResponse])
def list_chatbots(db: Session = Depends(get_db)):
    """List all chatbots for current user"""
    from models.chatbot import Chatbot
    
    chatbots = db.query(Chatbot).filter(Chatbot.user_id == 1).all()
    return chatbots


@router.get("/chatbots/{chatbot_id}", response_model=ChatbotResponse)
def get_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Get chatbot details"""
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    return chatbot


@router.put("/chatbots/{chatbot_id}", response_model=ChatbotResponse)
def update_chatbot(chatbot_id: int, chatbot_data: ChatbotUpdate, db: Session = Depends(get_db)):
    """Update chatbot configuration"""
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    update_data = chatbot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chatbot, field, value)
    
    db.commit()
    db.refresh(chatbot)
    
    return chatbot


@router.delete("/chatbots/{chatbot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chatbot(chatbot_id: int, db: Session = Depends(get_db)):
    """Delete a chatbot"""
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    db.delete(chatbot)
    db.commit()
    
    return None


# ============== Agent Routes ==============

@router.post("/chatbots/{chatbot_id}/agents", response_model=ChatbotAgentResponse)
def create_agent(chatbot_id: int, agent_data: ChatbotAgentCreate, db: Session = Depends(get_db)):
    """Add agent to chatbot"""
    from models.chatbot_agent import ChatbotAgent
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    agent = ChatbotAgent(chatbot_id=chatbot_id, **agent_data.dict())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent


@router.get("/chatbots/{chatbot_id}/agents", response_model=List[ChatbotAgentResponse])
def list_agents(chatbot_id: int, db: Session = Depends(get_db)):
    """List all agents for a chatbot"""
    from models.chatbot_agent import ChatbotAgent
    
    agents = db.query(ChatbotAgent).filter(ChatbotAgent.chatbot_id == chatbot_id).all()
    return agents


# ============== Node Routes ==============

@router.post("/chatbots/{chatbot_id}/nodes", response_model=ChatbotNodeResponse)
def create_node(chatbot_id: int, node_data: ChatbotNodeCreate, db: Session = Depends(get_db)):
    """Add node to chatbot graph"""
    from models.chatbot_node import ChatbotNode
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    node = ChatbotNode(chatbot_id=chatbot_id, **node_data.dict())
    db.add(node)
    db.commit()
    db.refresh(node)
    
    return node


@router.get("/chatbots/{chatbot_id}/nodes", response_model=List[ChatbotNodeResponse])
def list_nodes(chatbot_id: int, db: Session = Depends(get_db)):
    """List all nodes for a chatbot"""
    from models.chatbot_node import ChatbotNode
    
    nodes = db.query(ChatbotNode).filter(ChatbotNode.chatbot_id == chatbot_id).all()
    return nodes


# ============== Tool Routes ==============

@router.post("/chatbots/{chatbot_id}/tools", response_model=ChatbotToolResponse)
def create_tool(chatbot_id: int, tool_data: ChatbotToolCreate, db: Session = Depends(get_db)):
    """Add tool to chatbot"""
    from models.chatbot_tool import ChatbotTool
    from models.chatbot import Chatbot
    
    chatbot = db.query(Chatbot).filter(Chatbot.id == chatbot_id).first()
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    
    tool = ChatbotTool(chatbot_id=chatbot_id, **tool_data.dict())
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    return tool


@router.get("/chatbots/{chatbot_id}/tools", response_model=List[ChatbotToolResponse])
def list_tools(chatbot_id: int, db: Session = Depends(get_db)):
    """List all tools for a chatbot"""
    from models.chatbot_tool import ChatbotTool
    
    tools = db.query(ChatbotTool).filter(ChatbotTool.chatbot_id == chatbot_id).all()
    return tools


# ============== Chat Endpoint (Static Token Auth) ==============

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_static_token),
    chatbot=Depends(get_chatbot_by_token)
):
    """
    Chat with AI chatbot using static token authentication
    This endpoint is separate from WhatsApp automation
    """
    import time
    start_time = time.time()
    
    from services.langgraph_engine import LangGraphEngine
    from models.conversation import Conversation
    from models.chat_message import ChatMessage
    
    # Get or create conversation
    conversation = None
    if chat_request.session_id:
        conversation = db.query(Conversation).filter(
            Conversation.session_id == chat_request.session_id
        ).first()
    
    if not conversation:
        conversation = Conversation(
            chatbot_id=chatbot.id,
            user_id=chatbot.user_id,
            session_id=chat_request.session_id or f"sess_{int(time.time())}"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Process chat through LangGraph
    engine = LangGraphEngine(db, chatbot)
    response = await engine.process_message(
        conversation_id=conversation.id,
        message=chat_request.message,
        metadata=chat_request.metadata
    )
    
    # Save message to database
    message = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=response["content"],
        total_tokens=response["tokens_used"]
    )
    db.add(message)
    
    # Update conversation stats
    conversation.message_count += 1
    conversation.total_tokens_used += response["tokens_used"]
    conversation.last_message_at = time.strftime('%Y-%m-%d %H:%M:%S')
    db.commit()
    
    response_time_ms = (time.time() - start_time) * 1000
    
    return ChatResponse(
        conversation_id=conversation.id,
        message=ChatMessageResponse(
            id=message.id,
            conversation_id=conversation.id,
            role="assistant",
            content=response["content"],
            message_type="text",
            total_tokens=response["tokens_used"]
        ),
        tokens_used=response["tokens_used"],
        response_time_ms=response_time_ms
    )


# ============== Conversation Routes ==============

@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(chatbot_id: int = None, db: Session = Depends(get_db)):
    """List conversations"""
    from models.conversation import Conversation
    
    query = db.query(Conversation).filter(Conversation.user_id == 1)
    if chatbot_id:
        query = query.filter(Conversation.chatbot_id == chatbot_id)
    
    return query.all()


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get conversation details"""
    from models.conversation import Conversation
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation
