from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.middleware import require_admin
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/config", tags=["configuration"])

class BotConfigUpdate(BaseModel):
    bot_name: Optional[str] = None
    default_greeting: Optional[str] = None
    system_prompt: Optional[str] = None
    blacklisted_topics: Optional[str] = None
    max_clarifying_questions: Optional[int] = None
    escalation_message: Optional[str] = None
    voice_model: Optional[str] = None
    stt_model: Optional[str] = None
    chat_response_length: Optional[str] = None

class WidgetConfigUpdate(BaseModel):
    primary_color: Optional[str] = None
    position: Optional[str] = None
    greeting_message: Optional[str] = None
    channels_enabled: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/bot")
async def get_bot_config(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    client_id = current_user["user"]["client_id"]
    query = text("SELECT * FROM bot_config WHERE client_id = :client_id")
    result = await db.execute(query, {"client_id": client_id})
    row = result.fetchone()
    
    if not row:
        # Create default config if not exists
        insert_query = text("""
            INSERT INTO bot_config (client_id, bot_name, default_greeting, system_prompt)
            VALUES (:client_id, 'Voicera Assistant', 'Hello! How can I help you today?', 'You are a helpful AI assistant.')
            RETURNING *
        """)
        result = await db.execute(insert_query, {"client_id": client_id})
        await db.commit()
        row = result.fetchone()
        
    return dict(row._mapping)

@router.patch("/bot")
async def update_bot_config(
    config: BotConfigUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    client_id = current_user["user"]["client_id"]
    
    # Build dynamic update query
    update_data = config.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
    update_data["client_id"] = client_id
    
    query = text(f"UPDATE bot_config SET {set_clause} WHERE client_id = :client_id")
    await db.execute(query, update_data)
    await db.commit()
    
    return {"message": "Bot configuration updated successfully"}

@router.get("/widget")
async def get_widget_config(
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    client_id = current_user["user"]["client_id"]
    query = text("SELECT * FROM widget_config WHERE client_id = :client_id")
    result = await db.execute(query, {"client_id": client_id})
    row = result.fetchone()
    
    if not row:
        # Create default config if not exists
        insert_query = text("""
            INSERT INTO widget_config (client_id, primary_color, position, greeting_message)
            VALUES (:client_id, '#4ADE80', 'bottom-right', 'Hi! Need any help?')
            RETURNING *
        """)
        result = await db.execute(insert_query, {"client_id": client_id})
        await db.commit()
        row = result.fetchone()
        
    return dict(row._mapping)

@router.patch("/widget")
async def update_widget_config(
    config: WidgetConfigUpdate,
    current_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    client_id = current_user["user"]["client_id"]
    
    update_data = config.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
    update_data["client_id"] = client_id
    
    query = text(f"UPDATE widget_config SET {set_clause} WHERE client_id = :client_id")
    await db.execute(query, update_data)
    await db.commit()
    
    return {"message": "Widget configuration updated successfully"}
