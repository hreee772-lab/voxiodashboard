from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/voice", tags=["voice"])

@router.get("/token")
async def get_voice_token():
    return {"token": settings.DEEPGRAM_API_KEY}
