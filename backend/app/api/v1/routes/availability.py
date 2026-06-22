from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from datetime import time as TimeObj
from app.core.database import get_db
from app.core.middleware import get_current_user

router = APIRouter(prefix="/availability", tags=["availability"])

class AvailabilitySlot(BaseModel):
    day_of_week: int
    is_available: bool
    start_time: str
    end_time: str
    timezone: str = "Asia/Kolkata"

class AvailabilityUpdate(BaseModel):
    slots: List[AvailabilitySlot]

@router.get("/{specialist_id}")
async def get_availability(specialist_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            text("SELECT * FROM availability WHERE specialist_id = :id ORDER BY day_of_week"),
            {"id": specialist_id}
        )
        rows = result.fetchall()
        if not rows:
            # Return default availability
            return {"availability": [
                {"day_of_week": i, "is_available": True, 
                 "start_time": "09:00", "end_time": "18:00",
                 "timezone": "Asia/Kolkata"}
                for i in range(5)
            ]}
        return {"availability": [
            {"day_of_week": r.day_of_week, "is_available": r.is_available,
             "start_time": str(r.start_time)[:5], "end_time": str(r.end_time)[:5],
             "timezone": r.timezone or "Asia/Kolkata"}
            for r in rows
        ]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{specialist_id}")
async def update_availability(
    specialist_id: str,
    body: AvailabilityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Delete existing
        await db.execute(
            text("DELETE FROM availability WHERE specialist_id = :id"),
            {"id": specialist_id}
        )
        # Insert new
        for slot in body.slots:
            await db.execute(
                text("""INSERT INTO availability 
                    (specialist_id, day_of_week, is_available, start_time, end_time, timezone, updated_at)
                    VALUES (:sid, :day, :avail, :start, :end, :tz, NOW())"""),
                {
                    "sid": specialist_id,
                    "day": slot.day_of_week,
                    "avail": slot.is_available,
                    "start": TimeObj(*[int(x) for x in slot.start_time.split(":")[:2]]),
                    "end": TimeObj(*[int(x) for x in slot.end_time.split(":")[:2]]),
                    "tz": slot.timezone
                }
            )
        await db.commit()
        return {"message": "Availability updated successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
