"""
Caregiver's Fact-Check Companion


A WhatsApp bot that helps families research and debunk
misleading videos that worry vulnerable family members.


Supports: YouTube, TikTok
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routes import webhook_router
from app.config import settings




app = FastAPI(
    title="Caregiver's Fact-Check Companion",
    description="WhatsApp bot for researching misleading videos",
    version="1.0.0"
)


# CORS middleware (for any web dashboard later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(webhook_router, prefix="/api", tags=["webhook"])




@app.get("/")
async def root():
    return {
        "name": "Caregiver's Fact-Check Companion",
        "status": "running",
        "endpoints": {
            "webhook": "/api/webhook",
            "health": "/health"
        }
    }




@app.get("/health")
async def health():
    """Health check endpoint for deployment platforms."""
    return {
        "status": "healthy",
        "services": {
            "google_factcheck": bool(settings.GOOGLE_API_KEY),
            "openrouter": bool(settings.OPENROUTER_API_KEY),
            "serper": bool(settings.SERPER_API_KEY),
            "twilio": bool(settings.TWILIO_ACCOUNT_SID),
        }
    }




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )





