from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.conversation import router as conversation_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.meeting_state import router as meeting_state_router
from app.api.routes.questions import router as questions_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="MeetBridge AI backend API scaffold",
)

app.include_router(questions_router, prefix=settings.api_prefix)
app.include_router(conversation_router, prefix=settings.api_prefix)
app.include_router(meeting_state_router, prefix=settings.api_prefix)
app.include_router(knowledge_router, prefix=settings.api_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


@app.get(settings.api_prefix + "/health")
def api_health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
