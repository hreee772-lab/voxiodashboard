from fastapi import APIRouter, Depends, HTTPException, Request, Query, BackgroundTasks
from fastapi.responses import RedirectResponse
from app.services.calendar_service import calendar_service
from app.services.email_service import email_service
from app.core.config import settings
from pydantic import BaseModel
from typing import Optional
from supabase import create_client, Client
from datetime import datetime

from app.core.middleware import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/calendar", tags=["calendar"])

def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

class BookingRequest(BaseModel):
    specialist_id: str
    slot_start: str
    user_name: str
    user_email: str
    issue_summary: str
    session_id: str
    ticket_id: str

@router.get("/auth/{specialist_id}")
async def get_auth_url(specialist_id: str):
    auth_url = calendar_service.get_auth_url(specialist_id)
    return {"auth_url": auth_url}

@router.get("/callback", include_in_schema=False)
async def google_oauth_callback(request: Request):
    code = request.query_params.get("code")
    specialist_id = request.query_params.get("state") # We passed this in get_auth_url

    if not code or not specialist_id:
        raise HTTPException(status_code=400, detail="Invalid callback parameters")

    await calendar_service.exchange_code_for_tokens(code, specialist_id)
    
    # Redirect to dashboard success page
    dashboard_url = "https://voicera-dashboard.teamvoicera7.workers.dev/index?calendar=connected"
    return RedirectResponse(url=dashboard_url)


@router.get("/slots/{specialist_id}")
async def get_slots(specialist_id: str):
    slots = await calendar_service.get_available_slots(specialist_id)
    return {"slots": slots}


@router.get("/status")
async def get_calendar_status(current_user: dict = Depends(get_current_user)):
    try:
        from supabase import create_client
        from app.core.config import settings
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        
        client_id = current_user.get("client_id") or current_user.get("user", {}).get("client_id")
        
        res = supabase.table("integrations").select("id,is_active").eq("client_id", client_id).eq("crm_type", "google_calendar").execute()
        
        connected = len(res.data) > 0 and res.data[0].get("is_active", False)
        return {"connected": connected, "client_id": str(client_id)}
    except Exception as e:
        return {"connected": False, "error": str(e)}

@router.post("/book")
async def book_appointment(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        specialist_id = body.get("specialist_id")
        slot_start = body.get("slot_start")
        slot_end = body.get("slot_end")
        user_name = body.get("user_name", "Customer")
        user_email = body.get("user_email", "")
        issue_summary = body.get("issue_summary", "Support request")

        if not all([specialist_id, slot_start, slot_end]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        result = await calendar_service.book_appointment(
            specialist_id, slot_start, slot_end,
            user_name, user_email, issue_summary
        )

        # Save booking to database
        try:
            from sqlalchemy import text
            from app.core.database import get_db
            
            # Get specialist's client_id
            from supabase import create_client
            from app.core.config import settings
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            spec_res = supabase.table("users").select("client_id").eq("id", specialist_id).execute()
            client_id = spec_res.data[0]["client_id"] if spec_res.data else None
            
            if client_id:
                supabase.table("bookings").insert({
                    "client_id": str(client_id),
                    "specialist_id": str(specialist_id),
                    "customer_name": user_name,
                    "customer_email": user_email,
                    "scheduled_at": slot_start,
                    "slot_end": slot_end,
                    "meet_link": result.get("meet_link"),
                    "calendar_event_id": result.get("event_id"),
                    "status": "scheduled"
                }).execute()
        except Exception as db_err:
            print(f"Save booking error: {db_err}")

        # Send email to specialist via Brevo
        try:
            from app.services.email_service import send_booking_email
            # Get specialist email
            from supabase import create_client
            from app.core.config import settings
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
            spec_res = supabase.table("users").select("email,full_name").eq("id", specialist_id).execute()
            if spec_res.data:
                spec_email = spec_res.data[0]["email"]
                spec_name = spec_res.data[0]["full_name"]
                await send_booking_email(
                    to_email=spec_email,
                    to_name=spec_name,
                    customer_name=user_name,
                    customer_email=user_email,
                    slot_start=slot_start,
                    meet_link=result.get("meet_link"),
                    is_specialist=True
                )
            # Send to customer
            if user_email:
                await send_booking_email(
                    to_email=user_email,
                    to_name=user_name,
                    customer_name=user_name,
                    customer_email=user_email,
                    slot_start=slot_start,
                    meet_link=result.get("meet_link"),
                    is_specialist=False
                )
        except Exception as email_err:
            print(f"Email error: {email_err}")

        return {
            "success": True,
            "meet_link": result.get("meet_link"),
            "event_id": result.get("event_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bookings")
async def get_bookings(current_user: dict = Depends(get_current_user)):
    try:
        from supabase import create_client
        from app.core.config import settings
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        
        if "user" in current_user:
            client_id = current_user["user"].get("client_id")
            user_role = current_user["user"].get("role")
            user_id = current_user["user"].get("id")
        else:
            client_id = current_user.get("client_id")
            user_role = current_user.get("role")
            user_id = current_user.get("user_id")
        
        query = supabase.table("bookings").select("*").eq("client_id", str(client_id)).order("scheduled_at", desc=False)
        
        # Specialists only see their own bookings
        if user_role == "specialist":
            query = query.eq("specialist_id", str(user_id))
        
        res = query.execute()
        return {"bookings": res.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
