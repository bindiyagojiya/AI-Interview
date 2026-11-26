from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, questions, interviews

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Profiles"])
api_router.include_router(questions.router, prefix="/questions", tags=["Question Bank"])
api_router.include_router(interviews.router, prefix="/interviews", tags=["Interview Sessions"])

