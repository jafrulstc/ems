from fastapi import APIRouter
from app.api.routers import auth, tenant, academic, student, exam

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenant.router, tags=["tenant"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(exam.router, prefix="/exam", tags=["exam"])
