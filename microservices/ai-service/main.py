"""
AI Service - AI-powered auto-replies with token management
Handles: auto-reply, token deduction, AI integration
"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import random

from shared.database import get_db
from shared.models import AutoReply, TokenBalance, User, WhatsAppAccount
from shared.schemas import AutoReplyCreate, AutoReplyResponse, AIRequest, AIResponse
from shared.utils import calculate_token_cost, estimate_ai_tokens
from shared.config import settings

app = FastAPI(title="AI Service", version="1.0.0")


class AIEngine:
    """Mock AI engine for generating responses"""
    
    def __init__(self):
        self.providers = {
            "openai": self._mock_openai,
            "anthropic": self._mock_anthropic,
            "local": self._mock_local
        }
    
    async def generate_response(
        self,
        message: str,
        context: Optional[str] = None,
        max_tokens: int = 100,
        provider: str = "openai"
    ) -> dict:
        """Generate AI response"""
        if provider not in self.providers:
            raise HTTPException(status_code=400, detail=f"Unknown AI provider: {provider}")
        
        return await self.providers[provider](message, context, max_tokens)
    
    async def _mock_openai(self, message: str, context: str, max_tokens: int) -> dict:
        """Mock OpenAI response"""
        # Simulate AI processing
        response_text = self._generate_contextual_response(message, context)
        tokens_used = estimate_ai_tokens(response_text)
        cost = calculate_token_cost(tokens_used, settings.TOKEN_MARKUP_PRICE)
        
        return {
            "response": response_text,
            "tokens_used": tokens_used,
            "cost": cost,
            "provider": "openai"
        }
    
    async def _mock_anthropic(self, message: str, context: str, max_tokens: int) -> dict:
        """Mock Anthropic response"""
        response_text = self._generate_contextual_response(message, context)
        tokens_used = estimate_ai_tokens(response_text)
        cost = calculate_token_cost(tokens_used, settings.TOKEN_MARKUP_PRICE)
        
        return {
            "response": response_text,
            "tokens_used": tokens_used,
            "cost": cost,
            "provider": "anthropic"
        }
    
    async def _mock_local(self, message: str, context: str, max_tokens: int) -> dict:
        """Mock local model response"""
        response_text = self._generate_contextual_response(message, context)
        tokens_used = estimate_ai_tokens(response_text)
        # Local models are cheaper
        cost = calculate_token_cost(tokens_used, 5.0)
        
        return {
            "response": response_text,
            "tokens_used": tokens_used,
            "cost": cost,
            "provider": "local"
        }
    
    def _generate_contextual_response(self, message: str, context: Optional[str]) -> str:
        """Generate contextual response (mock)"""
        responses = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! Feel free to ask me anything."
            ],
            "pricing": [
                "Our pricing starts at $10/month. Would you like more details?",
                "We offer flexible pricing plans. Let me know what features you need!",
                "Check out our website for detailed pricing information."
            ],
            "support": [
                "I'm here to help! What issue are you experiencing?",
                "Let me assist you with that. Can you provide more details?",
                "Our support team is ready to help. What's the problem?"
            ],
            "default": [
                "Thanks for your message! I'll get back to you soon.",
                "I received your message. How can I assist you?",
                "Thank you for contacting us. What would you like to know?"
            ]
        }
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            category = "greeting"
        elif any(word in message_lower for word in ["price", "cost", "payment", "buy", "purchase"]):
            category = "pricing"
        elif any(word in message_lower for word in ["help", "support", "issue", "problem", "error"]):
            category = "support"
        else:
            category = "default"
        
        return random.choice(responses[category])


ai_engine = AIEngine()


@app.post("/auto-reply/configure", response_model=AutoReplyResponse)
async def configure_auto_reply(
    reply_data: AutoReplyCreate,
    db: Session = Depends(get_db)
):
    """Configure auto-reply for a WhatsApp account"""
    db_reply = AutoReply(
        user_id=1,  # Would come from JWT
        whatsapp_account_id=reply_data.whatsapp_account_id,
        trigger_keyword=reply_data.trigger_keyword,
        reply_message=reply_data.reply_message,
        use_ai=reply_data.use_ai,
        is_active=reply_data.is_active
    )
    
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    
    return db_reply


@app.get("/auto-reply", response_model=List[AutoReplyResponse])
async def list_auto_replies(
    user_id: int,
    whatsapp_account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List all auto-reply configurations"""
    query = db.query(AutoReply).filter(AutoReply.user_id == user_id)
    
    if whatsapp_account_id:
        query = query.filter(AutoReply.whatsapp_account_id == whatsapp_account_id)
    
    replies = query.all()
    return replies


@app.post("/auto-reply/process")
async def process_incoming_message(
    message: str,
    sender: str,
    whatsapp_account_id: int,
    db: Session = Depends(get_db)
):
    """Process incoming message and generate auto-reply"""
    # Find matching auto-reply rules
    auto_replies = db.query(AutoReply).filter(
        AutoReply.whatsapp_account_id == whatsapp_account_id,
        AutoReply.is_active == True
    ).all()
    
    matched_rule = None
    
    # Check for keyword matches
    for rule in auto_replies:
        if rule.trigger_keyword and rule.trigger_keyword.lower() in message.lower():
            matched_rule = rule
            break
    
    if not matched_rule:
        # Use default AI if enabled for any rule
        ai_rules = [r for r in auto_replies if r.use_ai]
        if ai_rules:
            matched_rule = ai_rules[0]
    
    if not matched_rule:
        return {
            "reply": None,
            "used_ai": False,
            "tokens_used": 0,
            "cost": 0
        }
    
    # Generate reply
    if matched_rule.use_ai:
        # Check token balance
        token_balance = db.query(TokenBalance).filter(
            TokenBalance.user_id == matched_rule.user_id
        ).first()
        
        if not token_balance or token_balance.balance <= 0:
            raise HTTPException(
                status_code=402,
                detail="Insufficient token balance. Please top up."
            )
        
        # Generate AI response
        ai_response = await ai_engine.generate_response(
            message=message,
            context=f"Conversation with {sender}",
            max_tokens=100
        )
        
        # Deduct tokens
        cost = ai_response["cost"]
        if token_balance.balance >= cost:
            token_balance.balance -= cost
            token_balance.tokens_used += ai_response["tokens_used"]
            db.commit()
            
            return {
                "reply": ai_response["response"],
                "used_ai": True,
                "tokens_used": ai_response["tokens_used"],
                "cost": cost,
                "remaining_balance": token_balance.balance
            }
        else:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient balance. Required: ${cost}, Available: ${token_balance.balance}"
            )
    else:
        # Use predefined reply
        return {
            "reply": matched_rule.reply_message,
            "used_ai": False,
            "tokens_used": 0,
            "cost": 0
        }


@app.post("/ai/generate", response_model=AIResponse)
async def generate_ai_response(
    request: AIRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Generate AI response with token deduction"""
    # Check token balance
    token_balance = db.query(TokenBalance).filter(
        TokenBalance.user_id == user_id
    ).first()
    
    if not token_balance:
        raise HTTPException(status_code=404, detail="Token balance not found")
    
    # Estimate cost
    estimated_tokens = estimate_ai_tokens(request.message) * 2  # Input + output
    estimated_cost = calculate_token_cost(estimated_tokens, settings.TOKEN_MARKUP_PRICE)
    
    if token_balance.balance < estimated_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient balance. Estimated cost: ${estimated_cost:.2f}"
        )
    
    # Generate response
    ai_response = await ai_engine.generate_response(
        message=request.message,
        context=request.context,
        max_tokens=request.max_tokens
    )
    
    # Deduct actual cost
    actual_cost = ai_response["cost"]
    token_balance.balance -= actual_cost
    token_balance.tokens_used += ai_response["tokens_used"]
    db.commit()
    
    return AIResponse(
        response=ai_response["response"],
        tokens_used=ai_response["tokens_used"],
        cost=actual_cost
    )


@app.get("/token/balance/{user_id}")
async def get_token_balance(user_id: int, db: Session = Depends(get_db)):
    """Get user's token balance"""
    balance = db.query(TokenBalance).filter(TokenBalance.user_id == user_id).first()
    
    if not balance:
        raise HTTPException(status_code=404, detail="Token balance not found")
    
    return {
        "user_id": user_id,
        "balance": balance.balance,
        "tokens_used": balance.tokens_used,
        "last_updated": balance.last_updated
    }


@app.get("/token/pricing")
async def get_token_pricing():
    """Get current token pricing"""
    return {
        "base_price_per_1000": settings.TOKEN_BASE_PRICE,
        "markup_price_per_1000": settings.TOKEN_MARKUP_PRICE,
        "currency": "USD",
        "providers": {
            "openai": settings.TOKEN_MARKUP_PRICE,
            "anthropic": settings.TOKEN_MARKUP_PRICE,
            "local": 5.0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
