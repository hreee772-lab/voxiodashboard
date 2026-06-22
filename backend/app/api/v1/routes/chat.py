from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from pydantic import BaseModel
from typing import List, Optional, Dict
from supabase import create_client, Client
from openai import OpenAI

router = APIRouter(prefix="/chat", tags=["chat"])

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class ChatMessageRequest(BaseModel):
    session_id: str
    client_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

@router.post("/message")
async def send_chat_message(
    chat_request: ChatMessageRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        supabase = get_supabase()
        client_id = chat_request.client_id

        # Step 1: Load bot config for this client
        config_res = supabase.table("bot_config").select("*").eq("client_id", client_id).execute()
        config = config_res.data[0] if config_res.data else {}

        bot_name = config.get("bot_name") or "AI Assistant"
        system_prompt_custom = config.get("system_prompt") or ""
        blacklisted_topics = config.get("blacklisted_topics") or ""
        escalation_keywords = config.get("escalation_keywords") or "speak to human,agent,specialist,manager,cancel,refund"
        escalation_message = config.get("escalation_message") or "Let me connect you with a specialist."
        chat_response_length = config.get("chat_response_length") or "balanced"
        response_format = config.get("response_format") or "bullets"

        user_msg_lower = chat_request.message.lower()

        # Step 2: Check escalation keywords
        esc_words = [k.strip().lower() for k in escalation_keywords.split(",") if k.strip()]
        if any(k in user_msg_lower for k in esc_words):
            return {
                "response": escalation_message,
                "confident": True,
                "should_escalate": True,
                "session_id": chat_request.session_id,
                "chunks_found": 0,
                "ticket_id": None,
                "debug_path": "ESCALATION"
            }

        # Step 3: Check blacklisted topics
        black_words = [t.strip().lower() for t in blacklisted_topics.split(",") if t.strip()]
        if any(t in user_msg_lower for t in black_words):
            return {
                "response": "I'm not able to discuss that topic. Is there something else I can help you with?",
                "confident": True,
                "should_escalate": False,
                "session_id": chat_request.session_id,
                "chunks_found": 0,
                "ticket_id": None,
                "debug_path": "BLACKLISTED"
            }

        # Step 4: Search KB - vector search first
        kb_context = ""
        chunks_found = 0
        try:
            from app.services.kb_service import kb_service
            from app.services.embedding_service import embedding_service
            raw_chunks = await kb_service.search_chunks(
                db=db,
                client_id=client_id,
                query=chat_request.message,
                limit=12
            )
            def clean_chunk(text):
                import re
                text = re.sub(r'\n\s*\n', '\n', text)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()
            if raw_chunks:
                kb_context = "\n---\n".join([clean_chunk(c["content"]) for c in raw_chunks])
                chunks_found = len(raw_chunks)
        except Exception as e:
            print(f"Vector search error: {e}")

        # Step 5: Always run keyword search and combine with vector results
        existing_content = kb_context
        try:
            keywords = chat_request.message.lower().split()
            stop_words = {'what','is','the','a','an','to','for','of','and','or','in','on','at','have','your','how','does','do'}
            clean_keywords = [k for k in keywords if k not in stop_words and len(k) > 2]
            chunks = []
            if clean_keywords:
                for kw in clean_keywords[:4]:
                    res = supabase.table("kb_chunks")\
                        .select("content")\
                        .eq("client_id", client_id)\
                        .ilike("content", f"%{kw}%")\
                        .limit(8).execute()
                    if res.data:
                        chunks.extend(res.data)
                        if len(chunks) >= 12:
                            break
            if chunks:
                keyword_context = "\n---\n".join([clean_chunk(c["content"]) for c in chunks])
                if existing_content and keyword_context:
                    kb_context = existing_content + "\n---\n" + keyword_context
                elif keyword_context:
                    kb_context = keyword_context
                chunks_found = chunks_found + len(chunks)
        except Exception as kw_err:
            print(f"Keyword search error: {kw_err}")

        # Step 6: Build format instructions from bot_config
        length_map = {
            "concise": "Keep your response to 1-2 sentences only. Be very brief.",
            "balanced": "Keep your response to 3-4 sentences maximum.",
            "detailed": "You can provide a detailed response with full explanation."
        }
        format_map = {
            "plain": "Use plain text only. No bullet points or markdown.",
            "bullets": "Use bullet points when listing 3 or more items. Use plain text otherwise.",
            "rich": "Use bullet points and **bold** for important terms when helpful."
        }
        length_instruction = length_map.get(chat_response_length, "Keep response concise.")
        format_instruction = format_map.get(response_format, "Use plain text only.")

        # Step 7: Build system prompt entirely from bot_config
        if system_prompt_custom:
            system_prompt = f"""{system_prompt_custom}

===KNOWLEDGE BASE===
{kb_context if kb_context else "No information found."}
===END KNOWLEDGE BASE===

IMPORTANT: The knowledge base above contains the answer. Extract and use the specific information from it. Do not say the knowledge base does not have information if the above section contains relevant content. {length_instruction} {format_instruction}"""
        else:
            system_prompt = f"""You are {bot_name}, a helpful customer support assistant.

===KNOWLEDGE BASE===
{kb_context if kb_context else "No information found."}
===END KNOWLEDGE BASE===

IMPORTANT RULES:
1. The knowledge base above contains information to answer the user's question.
2. Extract specific facts, points, and details from the knowledge base and include them in your response.
3. Do NOT say "the knowledge base does not specify" if the knowledge base section above has relevant content.
4. {length_instruction}
5. {format_instruction}
6. Never mention GPT, OpenAI or Claude.
7. If truly no relevant information exists in the knowledge base, offer to connect with a specialist."""

        # Step 8: Call OpenAI
        oai = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = oai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *(chat_request.conversation_history[-6:] if chat_request.conversation_history else []),
                {"role": "user", "content": chat_request.message}
            ],
            temperature=0.3,
            max_tokens=600
        )
        bot_text = response.choices[0].message.content

        return {
            "response": bot_text,
            "confident": bool(kb_context),
            "should_escalate": not bool(kb_context),
            "session_id": chat_request.session_id,
            "chunks_found": chunks_found,
            "ticket_id": None,
            "debug_path": "BOT_CONFIG_CLEAN"
        }

    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "response": "I'm having trouble right now. Please try again or ask to speak with a specialist.",
            "confident": False,
            "should_escalate": True,
            "session_id": chat_request.session_id,
            "chunks_found": 0,
            "ticket_id": None,
            "debug_path": "ERROR"
        }
