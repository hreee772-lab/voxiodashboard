from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.database import async_session
from app.services.bot_service import bot_service
import json
import time

router = APIRouter(prefix="/voice-llm", tags=["voice-llm"])

@router.get("/chat/completions")
async def voice_llm_health():
    return {"status": "ok", "model": "gpt-4o-mini"}

@router.post("/chat/completions")
async def voice_llm_completion(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    stream = body.get("stream", False)
    
    client_id = "70d0188f-ef36-4c79-b0b6-b215e767d859"
    
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break
    
    if not user_message:
        user_message = "Hello"
    
    conversation_history = []
    for msg in messages:
        if msg.get("role") in ["user", "assistant"]:
            conversation_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    async with async_session() as db:
        bot_response = await bot_service.get_bot_response(
            db=db,
            client_id=client_id,
            user_message=user_message,
            conversation_history=conversation_history[:-1]
        )
    
    response_text = bot_response.get("response", "I could not process that.")
    
    if stream:
        async def generate():
            chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [{
                    "index": 0,
                    "delta": {"role": "assistant", "content": response_text},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            
            done_chunk = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "gpt-4o-mini",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(done_chunk)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    return JSONResponse({
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4o-mini",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": response_text},
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })
