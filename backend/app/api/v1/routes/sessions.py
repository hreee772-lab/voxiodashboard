from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from app.core.middleware import get_current_user, require_admin
from app.core.config import settings
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from app.services.learning_service import learning_service
from app.services.email_service import email_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class SessionStartRequest(BaseModel):
    client_id: str
    user_email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    channel: str = "chat" # chat or voice

class MessageAddRequest(BaseModel):
    role: str # user or assistant
    content: str
    metadata: Optional[Dict] = None

class SessionStatusUpdate(BaseModel):
    status: str # active, resolved, escalated, closed

class ResolveSessionRequest(BaseModel):
    client_id: str
    user_email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    issue_summary: Optional[str] = "No summary provided"

@router.post("/start")
async def start_session(request: SessionStartRequest):
    supabase = get_supabase()
    
    session_data = {
        "client_id": request.client_id,
        "customer_email": request.user_email,
        "customer_name": request.user_name,
        "channel": request.channel,
        "status": "active",
        "transcript": []
    }
    
    try:
        res = supabase.table("sessions").insert(session_data).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        row = res.data[0]
        return {
            "session_id": row["id"],
            "created_at": row["created_at"],
            "status": row["status"]
        }
    except Exception as e:
        print(f"DATABASE CONNECTION ERROR (Session Start): {e}")
        # MOCK FALLBACK
        import uuid
        from datetime import datetime
        return {
            "session_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }

@router.post("/{session_id}/message")
async def add_message(session_id: str, request: MessageAddRequest):
    supabase = get_supabase()
    
    # 1. Fetch current session to get existing transcript
    res = supabase.table("sessions").select("transcript").eq("id", session_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    current_transcript = res.data[0].get("transcript") or []
    
    # 2. Append new message
    new_message = {
        "role": request.role,
        "content": request.content,
        "metadata": request.metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    current_transcript.append(new_message)
    
    # 3. Update session
    update_res = supabase.table("sessions").update({
        "transcript": current_transcript
    }).eq("id", session_id).execute()
    
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update session messages")
    
    return {
        "message_id": len(current_transcript), # Mock ID based on index
        "timestamp": new_message["timestamp"]
    }

@router.get("/{session_id}")
async def get_session_detail(
    session_id: str,
    client_id: str = Query(...), # Required for isolation
    current_user: Optional[dict] = Depends(require_admin) # Optional, can be accessed by widget if client_id matches
):
    supabase = get_supabase()
    
    # If admin is logged in, verify they own the client
    if current_user:
        admin_client_id = str(current_user["user"]["client_id"])
        if admin_client_id != client_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to this client's sessions")

    res = supabase.table("sessions").select("*").eq("id", session_id).eq("client_id", client_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return res.data[0]

@router.get("")
async def list_sessions(
    status: Optional[str] = None,
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    
    # Handle both old and new token formats
    if "user" in current_user:
        client_id = str(current_user["user"]["client_id"])
    else:
        client_id = str(current_user.get("client_id", ""))
    
    if not client_id:
        raise HTTPException(status_code=400, detail="Client ID not found")
    
    query = supabase.table("sessions").select("*").eq("client_id", client_id)
    
    if status:
        query = query.eq("status", status)
    
    res = query.order("created_at", desc=True).limit(limit).execute()
    return {"sessions": res.data}

@router.patch("/{session_id}")
async def update_session(
    session_id: str, 
    request: SessionStatusUpdate,
    current_user: dict = Depends(require_admin)
):
    supabase = get_supabase()
    client_id = str(current_user["user"]["client_id"])
    
    # Verify ownership before update
    check_res = supabase.table("sessions").select("id").eq("id", session_id).eq("client_id", client_id).execute()
    if not check_res.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_res = supabase.table("sessions").update({
        "status": request.status
    }).eq("id", session_id).execute()
    
    if not update_res.data:
        raise HTTPException(status_code=500, detail="Failed to update session status")
    
    return update_res.data[0]

@router.post("/{session_id}/resolve")
async def resolve_session(
    session_id: str,
    request: ResolveSessionRequest,
    background_tasks: BackgroundTasks
):
    supabase = get_supabase()
    
    # 1. Update session status to 'resolved'
    session_update = supabase.table("sessions").update({
        "status": "resolved"
    }).eq("id", session_id).execute()
    
    if not session_update.data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_row = session_update.data[0]
    
    # 2. Update ticket status to 'resolved' where session_id matches
    supabase.table("tickets").update({
        "status": "resolved",
        "updated_at": datetime.utcnow().isoformat()
    }).eq("session_id", session_id).execute()
    
    # 3. Send resolution email via centralized service if email is provided
    if request.user_email:
        background_tasks.add_task(
            email_service.send_session_summary,
            user_name=request.user_name or 'there',
            user_email=request.user_email,
            issue_summary=request.issue_summary,
            session_id=session_id
        )
            
    # 4. Trigger auto-learning in background
    background_tasks.add_task(
        learning_service.auto_learn_from_resolution,
        session_id=session_id,
        client_id=request.client_id,
        conversation_history=session_row.get("transcript", [])
    )
    
    return {
        "status": "resolved",
        "session_id": session_id,
        "auto_learn_triggered": True
    }
