from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(prefix="/waitlist", tags=["waitlist"])

class WaitlistEntry(BaseModel):
    email: EmailStr
    source: str = "landing_page"

@router.post("")
async def join_waitlist(
    entry: WaitlistEntry,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Check if email already exists
        check_query = text("SELECT id FROM waitlist WHERE email = :email")
        result = await db.execute(check_query, {"email": entry.email})
        if result.fetchone():
            return {"message": "You are already on the waitlist!"}

        # Insert new entry
        insert_query = text("""
            INSERT INTO waitlist (email, source)
            VALUES (:email, :source)
            RETURNING id
        """)
        res = await db.execute(insert_query, {
            "email": entry.email,
            "source": entry.source
        })
        await db.commit()
        return {"message": "Successfully joined the waitlist!", "id": str(res.scalar())}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to join waitlist: {str(e)}")
