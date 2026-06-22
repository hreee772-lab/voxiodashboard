from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.middleware import get_current_user
from app.core.security import create_access_token
from supabase import create_client
from app.core.config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/superadmin", tags=["superadmin"])

def get_supabase():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

def require_superadmin(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role") or current_user.get("user", {}).get("role")
    if role not in ["super_admin"]:
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user

@router.get("/stats")
async def get_platform_stats(current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        now = datetime.utcnow()
        today = (now - timedelta(hours=24)).isoformat()
        week_ago = (now - timedelta(days=7)).isoformat()
        month_ago = (now - timedelta(days=30)).isoformat()

        clients = supabase.table("clients").select("id, plan, is_active, created_at").execute().data or []
        users = supabase.table("users").select("id, role, is_active, created_at").neq("email", "test@example.com").execute().data or []
        sessions = supabase.table("sessions").select("id, channel, status, created_at, client_id").execute().data or []
        tickets = supabase.table("tickets").select("id, status, created_at").execute().data or []
        bookings = supabase.table("bookings").select("id, status, created_at").execute().data or []
        kb_chunks = supabase.table("kb_chunks").select("id").execute().data or []
        kb_docs = supabase.table("kb_documents").select("id").execute().data or []

        active_sessions = [s for s in sessions if s.get("status") in ["active", "in_progress"]]
        resolved = [s for s in sessions if s.get("status") == "resolved"]
        resolution_rate = round((len(resolved) / len(sessions) * 100), 1) if sessions else 0

        return {
            "total_companies": len(clients),
            "active_companies": len([c for c in clients if c.get("is_active")]),
            "new_companies_this_week": len([c for c in clients if c.get("created_at", "") > week_ago]),
            "new_companies_this_month": len([c for c in clients if c.get("created_at", "") > month_ago]),
            "free_plan": len([c for c in clients if c.get("plan") == "free"]),
            "pro_plan": len([c for c in clients if c.get("plan") == "pro"]),
            "total_users": len(users),
            "total_sessions": len(sessions),
            "sessions_today": len([s for s in sessions if s.get("created_at", "") > today]),
            "sessions_this_week": len([s for s in sessions if s.get("created_at", "") > week_ago]),
            "active_sessions_now": len(active_sessions),
            "voice_sessions": len([s for s in sessions if s.get("channel") == "voice"]),
            "chat_sessions": len([s for s in sessions if s.get("channel") == "chat"]),
            "resolution_rate": resolution_rate,
            "total_tickets": len(tickets),
            "open_tickets": len([t for t in tickets if t.get("status") in ["open", "escalated"]]),
            "total_bookings": len(bookings),
            "scheduled_calls": len([b for b in bookings if b.get("status") == "scheduled"]),
            "total_kb_chunks": len(kb_chunks),
            "total_kb_documents": len(kb_docs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients")
async def get_all_clients(current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        clients = supabase.table("clients").select("*").order("created_at", desc=True).execute().data or []
        
        enriched = []
        for client in clients:
            cid = client["id"]
            sessions = supabase.table("sessions").select("id, created_at, status").eq("client_id", cid).execute().data or []
            tickets = supabase.table("tickets").select("id").eq("client_id", cid).execute().data or []
            users = supabase.table("users").select("id, role, is_active").eq("client_id", cid).neq("email", "test@example.com").execute().data or []
            kb_docs = supabase.table("kb_documents").select("id").eq("client_id", cid).execute().data or []
            
            last_activity = max([s["created_at"] for s in sessions], default=None) if sessions else None
            
            enriched.append({
                **client,
                "session_count": len(sessions),
                "ticket_count": len(tickets),
                "user_count": len(users),
                "kb_doc_count": len(kb_docs),
                "last_activity": last_activity,
                "active_sessions": len([s for s in sessions if s.get("status") in ["active", "in_progress"]])
            })
        
        return {"clients": enriched}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clients/{client_id}")
async def get_client_detail(client_id: str, current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        
        client_res = supabase.table("clients").select("*").eq("id", client_id).execute()
        if not client_res.data:
            raise HTTPException(status_code=404, detail="Client not found")
        
        users = supabase.table("users").select("*").eq("client_id", client_id).execute().data or []
        sessions = supabase.table("sessions").select("*").eq("client_id", client_id).order("created_at", desc=True).limit(20).execute().data or []
        tickets = supabase.table("tickets").select("*").eq("client_id", client_id).order("created_at", desc=True).limit(20).execute().data or []
        kb_docs = supabase.table("kb_documents").select("*").eq("client_id", client_id).execute().data or []
        bookings = supabase.table("bookings").select("*").eq("client_id", client_id).execute().data or []
        bot_config = supabase.table("bot_config").select("*").eq("client_id", client_id).execute().data
        
        return {
            "client": client_res.data[0],
            "users": users,
            "sessions": sessions,
            "tickets": tickets,
            "kb_documents": kb_docs,
            "bookings": bookings,
            "bot_config": bot_config[0] if bot_config else None,
            "stats": {
                "total_sessions": len(sessions),
                "total_tickets": len(tickets),
                "total_users": len(users),
                "kb_docs": len(kb_docs),
                "total_bookings": len(bookings)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/clients/{client_id}")
async def update_client(client_id: str, request: Request, current_user: dict = Depends(require_superadmin)):
    try:
        body = await request.json()
        supabase = get_supabase()
        allowed = ["plan", "is_active", "company_name"]
        update_data = {k: v for k, v in body.items() if k in allowed}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields")
        supabase.table("clients").update(update_data).eq("id", client_id).execute()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clients/{client_id}/impersonate")
async def impersonate_client(client_id: str, current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        admin = supabase.table("users").select("id, email, role").eq("client_id", client_id).eq("role", "admin").limit(1).execute().data
        if not admin:
            raise HTTPException(status_code=404, detail="No admin found for this client")
        user = admin[0]
        token = create_access_token(
            subject=user["email"],
            extra_data={"role": user["role"], "client_id": client_id, "email": user["email"], "user_id": str(user["id"])}
        )
        return {"access_token": token, "client_id": client_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_all_users(current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        users = supabase.table("users").select("id, email, full_name, role, is_active, created_at, client_id").neq("email", "test@example.com").order("created_at", desc=True).execute().data or []
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_all_sessions(limit: int = 100, client_id: str = None, channel: str = None, status: str = None, current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        query = supabase.table("sessions").select("*").order("created_at", desc=True).limit(limit)
        if client_id:
            query = query.eq("client_id", client_id)
        if channel:
            query = query.eq("channel", channel)
        if status:
            query = query.eq("status", status)
        sessions = query.execute().data or []
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets")
async def get_all_tickets(limit: int = 100, client_id: str = None, status: str = None, current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        query = supabase.table("tickets").select("*").order("created_at", desc=True).limit(limit)
        if client_id:
            query = query.eq("client_id", client_id)
        if status:
            query = query.eq("status", status)
        tickets = query.execute().data or []
        return {"tickets": tickets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/billing")
async def get_billing_overview(current_user: dict = Depends(require_superadmin)):
    try:
        supabase = get_supabase()
        clients = supabase.table("clients").select("id, company_name, company_email, plan, is_active, created_at").order("created_at", desc=True).execute().data or []
        
        billing = []
        for client in clients:
            sessions = supabase.table("sessions").select("id").eq("client_id", client["id"]).execute().data or []
            credits_used = len(sessions)
            credits_limit = 2000 if client.get("plan") == "free" else 50000
            
            billing.append({
                **client,
                "credits_used": credits_used,
                "credits_limit": credits_limit,
                "credits_percent": round((credits_used / credits_limit * 100), 1)
            })
        
        return {
            "billing": billing,
            "summary": {
                "total_free": len([c for c in clients if c.get("plan") == "free"]),
                "total_pro": len([c for c in clients if c.get("plan") == "pro"]),
                "total_revenue": len([c for c in clients if c.get("plan") == "pro"]) * 1350
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_system_health(current_user: dict = Depends(require_superadmin)):
    try:
        import httpx
        supabase = get_supabase()
        
        kb_chunks = supabase.table("kb_chunks").select("id", count="exact").execute()
        kb_docs = supabase.table("kb_documents").select("id", count="exact").execute()
        
        return {
            "backend_status": "healthy",
            "database_status": "connected",
            "total_kb_chunks": len(kb_chunks.data or []),
            "total_kb_documents": len(kb_docs.data or []),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "backend_status": "error",
            "database_status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
