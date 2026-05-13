"""
Academic feature router.
Aggregates sub-routers for setup (classes, sections, subjects) and student/enrollment management.
"""
from fastapi import APIRouter
from app.features.academic.routers.setup_router import router as setup_router
from app.features.academic.routers.student_router import router as student_router

router = APIRouter()

router.include_router(setup_router)
router.include_router(student_router)
