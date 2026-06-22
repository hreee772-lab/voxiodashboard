# Voicera Backend v1.2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

fastapi_app = FastAPI(
    title="Voicera Backend API",
    description="Backend for Voicera - AI-powered customer support platform",
    version="0.1.0",
)

# Set up CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://voicera-dashboard.teamvoicera7.workers.dev",
        "https://voicera-landing.teamvoicera7.workers.dev",
        "https://voicera-superadmin.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "voicera-backend"
    }

from app.api.v1.routes import (
    auth_router, kb_router, config_router, chat_router, 
    sessions_router, tickets_router, waitlist_router, calendar_router, voice_router, voice_llm_router,
    availability_router
)

fastapi_app.include_router(auth_router, prefix="/api/v1")
fastapi_app.include_router(kb_router, prefix="/api/v1")
fastapi_app.include_router(config_router, prefix="/api/v1")
fastapi_app.include_router(chat_router, prefix="/api/v1")
fastapi_app.include_router(sessions_router, prefix="/api/v1")
fastapi_app.include_router(tickets_router, prefix="/api/v1")
fastapi_app.include_router(waitlist_router, prefix="/api/v1")
fastapi_app.include_router(calendar_router, prefix="/api/v1")
fastapi_app.include_router(voice_router, prefix="/api/v1")
fastapi_app.include_router(voice_llm_router, prefix="/api/v1")
fastapi_app.include_router(availability_router, prefix="/api/v1")

from app.api.v1.routes.bot_config import router as bot_config_router
fastapi_app.include_router(bot_config_router, prefix="/api/v1")

from app.api.v1.routes.voice_kb import router as voice_kb_router
fastapi_app.include_router(voice_kb_router, prefix="/api/v1")

from app.api.v1.routes.superadmin import router as superadmin_router
fastapi_app.include_router(superadmin_router, prefix="/api/v1")


