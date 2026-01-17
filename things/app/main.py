"""Fact-Check Companion (Promptless Products)

Narrow domain: high-signal verification for a single top-tier performer who
needs to stay on top of their game when a link is making the rounds.

Promptless: no "is this true?" prompt-writing. Forward a link and get a short,
decision-ready brief.

Restraint: labels confidence and avoids over-claiming when evidence is thin.
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routes import webhook_router
from app.config import settings




app = FastAPI(
    title="Caregiver's Fact-Check Companion",
    description="High-signal, low-noise fact-check companion for shared videos",
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
            "openai": bool(settings.OPENAI_API_KEY),
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





