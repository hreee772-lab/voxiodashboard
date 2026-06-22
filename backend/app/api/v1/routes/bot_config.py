from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.middleware import get_current_user
from supabase import create_client
from app.core.config import settings

router = APIRouter(prefix="/bot-config", tags=["bot_config"])

def get_supabase():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

@router.get("/public")
async def get_public_bot_config(client_id: str):
    try:
        supabase = get_supabase()
        res = supabase.table("bot_config").select("*").eq("client_id", client_id).execute()
        
        if res.data:
            return {"config": res.data[0]}
        
        # Return defaults if no config exists
        return {"config": {
            "bot_name": "Voicera AI",
            "default_greeting": "Hi! How can I help you today?",
            "system_prompt": "You are a helpful customer support assistant.",
            "blacklisted_topics": "",
            "max_clarifying_questions": 3,
            "escalation_message": "Let me connect you with a specialist who can help.",
            "voice_model": "aura-asteria-en",
            "stt_model": "nova-2",
            "chat_response_length": "medium",
            "escalation_keywords": "speak to human, manager, cancel, lawsuit, refund",
            "voice_greeting": "",
            "chat_greeting": "",
            "response_format": "bullets"
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def get_bot_config(current_user: dict = Depends(get_current_user)):
    try:
        client_id = current_user.get("client_id") or current_user.get("user", {}).get("client_id")
        supabase = get_supabase()
        res = supabase.table("bot_config").select("*").eq("client_id", str(client_id)).execute()
        
        if res.data:
            return {"config": res.data[0]}
        
        # Return defaults if no config exists
        return {"config": {
            "bot_name": "Voicera AI",
            "default_greeting": "Hi! How can I help you today?",
            "system_prompt": "You are a helpful customer support assistant.",
            "blacklisted_topics": "",
            "max_clarifying_questions": 3,
            "escalation_message": "Let me connect you with a specialist who can help.",
            "voice_model": "aura-asteria-en",
            "stt_model": "nova-2",
            "chat_response_length": "medium",
            "escalation_keywords": "speak to human, manager, cancel, lawsuit, refund",
            "voice_greeting": "",
            "chat_greeting": "",
            "response_format": "bullets"
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def save_bot_config(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        client_id = current_user.get("client_id") or current_user.get("user", {}).get("client_id")
        body = await request.json()
        
        supabase = get_supabase()
        
        # Check if config exists
        existing = supabase.table("bot_config").select("id").eq("client_id", str(client_id)).execute()
        
        config_data = {
            "client_id": str(client_id),
            "bot_name": body.get("bot_name", "Voicera AI"),
            "default_greeting": body.get("default_greeting", "Hi! How can I help you today?"),
            "system_prompt": body.get("system_prompt", "You are a helpful customer support assistant."),
            "blacklisted_topics": body.get("blacklisted_topics", ""),
            "max_clarifying_questions": int(body.get("max_clarifying_questions", 3)),
            "escalation_message": body.get("escalation_message", "Let me connect you with a specialist."),
            "voice_model": body.get("voice_model", "aura-asteria-en"),
            "stt_model": body.get("stt_model", "nova-2"),
            "chat_response_length": body.get("chat_response_length", "medium"),
            "escalation_keywords": body.get("escalation_keywords", "speak to human, manager, cancel"),
            "voice_greeting": body.get("voice_greeting", ""),
            "chat_greeting": body.get("chat_greeting", ""),
            "response_format": body.get("response_format", "bullets")
        }
        
        if existing.data:
            supabase.table("bot_config").update(config_data).eq("client_id", str(client_id)).execute()
        else:
            supabase.table("bot_config").insert(config_data).execute()
        
        return {"success": True, "message": "Bot configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
