"""
Exam feature router.
Aggregates sub-routers for setup (types, boards, grading) and marking (registrations, marks, results).
"""
from fastapi import APIRouter
from app.features.exam.routers.setup_router import router as setup_router
from app.features.exam.routers.marking_router import router as marking_router

router = APIRouter()

router.include_router(setup_router)
router.include_router(marking_router)
