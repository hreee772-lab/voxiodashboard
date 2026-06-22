from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.middleware import require_admin, get_current_user
from app.core.config import settings
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["tickets"])

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class TicketCreateRequest(BaseModel):
    session_id: Optional[str] = None
    client_id: str
    user_email: EmailStr
    issue_summary: str
    conversation_transcript: Optional[List[Dict]] = None
    urgency: Optional[str] = None # low, medium, high

class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None # open, active, resolved, closed
    notes: Optional[str] = None

def calculate_urgency(summary: str, transcript: Optional[List[Dict]]) -> str:
    high_priority_keywords = ["cancel", "angry", "urgent", "emergency", "broken", "refund", "lawyer"]
    text_to_check = summary.lower()
    
    if transcript:
        for msg in transcript:
            text_to_check += " " + msg.get("content", "").lower()
            
    for word in high_priority_keywords:
        if word in text_to_check:
            return "high"
            
    return "medium"

@router.post("")
async def create_ticket(request: TicketCreateRequest):
    supabase = get_supabase()
    
    # Auto-assign urgency if not provided
    final_urgency = request.urgency
    if not final_urgency:
        final_urgency = calculate_urgency(request.issue_summary, request.conversation_transcript)
    
    ticket_data = {
        "client_id": request.client_id,
        "session_id": request.session_id,
        "customer_email": request.user_email,
        "issue_summary": request.issue_summary,
        "status": "open",
        # Storing transcript and urgency in metadata or notes since they might not be in base schema
        "notes": f"Urgency: {final_urgency}\n\nTranscript provided: {bool(request.conversation_transcript)}"
    }
    
    # If the user has added an 'urgency' column, we'd use it here. 
    # For now, we'll keep the insert compatible with the base schema.
    res = supabase.table("tickets").insert(ticket_data).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create ticket")
        
    row = res.data[0]
    return {
        "ticket_id": row["id"],
        "status": row["status"],
        "created_at": row["created_at"],
        "assigned_urgency": final_urgency
    }

@router.get("")
async def list_tickets(
    status: Optional[str] = None,
    limit: Optional[int] = 50,
    current_user: dict = Depends(get_current_user)
):
    supabase = get_supabase()
    
    if "user" in current_user:
        client_id = str(current_user["user"]["client_id"])
    else:
        client_id = str(current_user.get("client_id", ""))
        
    if not client_id:
        raise HTTPException(status_code=400, detail="Client ID not found")
    
    query = supabase.table("tickets").select("*").eq("client_id", client_id)
    
    if status:
        query = query.eq("status", status)
        
    res = query.order("created_at", desc=True).limit(limit).execute()
    return {"tickets": res.data}

@router.get("/{ticket_id}")
async def get_ticket_detail(
    ticket_id: str,
    current_user: dict = Depends(require_admin)
):
    supabase = get_supabase()
    client_id = str(current_user["user"]["client_id"])
    
    res = supabase.table("tickets").select("*, sessions(*)").eq("id", ticket_id).eq("client_id", client_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    return res.data[0]

@router.patch("/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    request: TicketUpdateRequest,
    current_user: dict = Depends(require_admin)
):
    supabase = get_supabase()
    client_id = str(current_user["user"]["client_id"])
    
    # Verify ownership
    check = supabase.table("tickets").select("id").eq("id", ticket_id).eq("client_id", client_id).execute()
    if not check.data:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    update_data = {}
    if request.status:
        update_data["status"] = request.status
        if request.status == "closed":
            update_data["closed_at"] = datetime.utcnow().isoformat()
            
    if request.notes:
        update_data["notes"] = request.notes
        
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    res = supabase.table("tickets").update(update_data).eq("id", ticket_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to update ticket")
        
    return res.data[0]
