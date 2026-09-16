import uuid
from collections import defaultdict
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import YearlyClassSubject
from app.models.exam import Exam, ExamResult, ExamSchedule, GradingScale


class ExamService:
    @staticmethod
    async def generate_exam_results(exam_id: uuid.UUID, session: AsyncSession) -> dict:
        """
        Optimised result generation — 5 fixed queries regardless of class/student count.

        Old approach: 1 query/schedule (enrollments) + 1 query/student (existing check)
                      → e.g. 6 subjects × 200 students = 1 206 queries
        New approach:
          Q1 – all active schedules for the exam
          Q2 – all active enrollments for the relevant class_ids  (batch .in_)
          Q3 – all existing ExamResult rows (any is_deleted)      (batch .in_)
          Q4 – grading scales
          Q5 – all active results for grade recalculation          (after flush)
        """
        from app.models.student import Enrollment

        # ── Q1: schedules ─────────────────────────────────────────────────────
        schedules = (
            await session.execute(
                select(ExamSchedule).where(
                    ExamSchedule.exam_id == exam_id,
                    ExamSchedule.is_deleted == False  # noqa: E712
                )
            )
        ).scalars().all()

        if not schedules:
            raise HTTPException(status_code=400, detail="No schedules found for this exam")

        schedule_ids = [s.id for s in schedules]
        schedule_map = {s.id: s for s in schedules}

        # class_id → [schedule, …]  (pure Python, no DB)
        class_to_schedules: dict[uuid.UUID, list] = defaultdict(list)
        for sched in schedules:
            class_to_schedules[sched.class_id].append(sched)
        class_ids = list(class_to_schedules.keys())

        # ── Q2: all enrollments for every relevant class (one batch query) ────
        enrollments = (
            await session.execute(
                select(Enrollment).where(
                    Enrollment.class_id.in_(class_ids),
                    Enrollment.is_deleted == False  # noqa: E712
                )
            )
        ).scalars().all()

        # ── Q3: existing result rows — deleted inclusive — for duplicate guard ─
        # NOTE: is_deleted is intentionally NOT filtered here.
        # A soft-deleted row still "owns" the (enrollment, schedule) slot and
        # must not be recreated (that was the original source of duplicates).
        existing_rows = (
            await session.execute(
                select(ExamResult).where(
                    ExamResult.exam_schedule_id.in_(schedule_ids)
                )
            )
        ).scalars().all()
        existing_pairs: set[tuple[uuid.UUID, uuid.UUID]] = {
            (r.enrollment_id, r.exam_schedule_id) for r in existing_rows
        }

        # ── Bulk-create missing result rows (single session.add_all) ──────────
        new_results: list[ExamResult] = []
        for enrollment in enrollments:
            for sched in class_to_schedules[enrollment.class_id]:
                if (enrollment.id, sched.id) not in existing_pairs:
                    new_results.append(
                        ExamResult(
                            enrollment_id=enrollment.id,
                            exam_schedule_id=sched.id,
                            obtained_marks=0.0,
                            grade=None,
                            status="PRESENT",
                            tenant_id=enrollment.tenant_id,
                        )
                    )

        if new_results:
            session.add_all(new_results)
        # flush so newly inserted rows are visible to Q5 below
        await session.flush()

        # ── Q4: grading scales ────────────────────────────────────────────────
        scales = (
            await session.execute(
                select(GradingScale).where(GradingScale.is_deleted == False)  # noqa: E712
            )
        ).scalars().all()
        sorted_scales = sorted(scales, key=lambda s: s.min_marks, reverse=True)

        # ── Q5: all active results for grade recalculation ────────────────────
        all_active = (
            await session.execute(
                select(ExamResult).where(
                    ExamResult.exam_schedule_id.in_(schedule_ids),
                    ExamResult.is_deleted == False  # noqa: E712
                )
            )
        ).scalars().all()

        # ── Recalculate grades purely in Python — zero extra DB queries ───────
        updated_count = 0
        for res in all_active:
            schedule = schedule_map.get(res.exam_schedule_id)
            if not schedule or schedule.full_marks == 0:
                continue

            status = res.status or "PRESENT"

            if status != "PRESENT":
                # ABSENT / WITHHELD / EXPELLED → use status as grade marker
                assigned_grade = status
            else:
                pct = (res.obtained_marks / schedule.full_marks) * 100
                assigned_grade = None
                for scale in sorted_scales:   # already sorted desc
                    if pct >= scale.min_marks:
                        assigned_grade = scale.grade_name
                        break

            if assigned_grade and res.grade != assigned_grade:
                res.grade = assigned_grade
                updated_count += 1

        await session.commit()
        return {
            "message": (
                f"Done. Created {len(new_results)} missing result rows, "
                f"updated grades for {updated_count} results."
            )
        }

    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    async def validate_class_subject(
        class_id: uuid.UUID,
        subject_id: uuid.UUID,
        exam_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        from app.models.academic import YearlyClassSubject

        exam = await session.get(Exam, exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        stmt = select(YearlyClassSubject).where(
            YearlyClassSubject.class_id == class_id,
            YearlyClassSubject.subject_id == subject_id,
            YearlyClassSubject.academic_year_id == exam.academic_year_id,
        )
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="This subject is not assigned to this class for the exam's academic year.",
            )

    @staticmethod
    async def get_exam_assigned_subjects(exam_id: uuid.UUID, session: AsyncSession) -> list[uuid.UUID]:
        exam = await session.get(Exam, exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")

        stmt = select(YearlyClassSubject.subject_id).where(
            YearlyClassSubject.academic_year_id == exam.academic_year_id
        ).distinct()

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_exam_merit_list(
        session: AsyncSession,
        exam_id: uuid.UUID | None = None,
        academic_year_id: uuid.UUID | None = None,
        class_id: uuid.UUID | None = None,
    ) -> list[dict]:
        from app.models.academic import (
            AcademicClass,
            AcademicYear,
            Subject,
            YearlyClassSubject,
        )
        from app.models.exam import GradingScale
        from app.models.student import Enrollment, Student

        scales = (await session.execute(select(GradingScale))).scalars().all()
        grade_to_point = {scale.grade_name: scale.grade_point for scale in scales}
        failing_grades = {
            scale.grade_name
            for scale in scales
            if hasattr(scale, "is_pass") and not scale.is_pass
        }

        fail_grade_name = "F"
        for scale in scales:
            if scale.min_marks <= 0 <= scale.max_marks:
                fail_grade_name = scale.grade_name
                break

        stmt = select(
            ExamResult.enrollment_id,
            ExamResult.obtained_marks,
            ExamResult.grade,
            ExamResult.status,
            ExamSchedule.full_marks,
            YearlyClassSubject.affects_result_calculation,
            Enrollment.class_id,
            Enrollment.academic_year_id,
            Enrollment.roll_number,
            Student.full_name,
            Student.student_id_no,
            AcademicClass.name.label("class_name"),
            AcademicYear.name.label("academic_year_name"),
            Exam.name.label("exam_name"),
            Exam.id.label("exam_id"),
            Subject.name.label("subject_name"),
        ).join(
            Enrollment, ExamResult.enrollment_id == Enrollment.id
        ).join(
            Student, Enrollment.student_id == Student.id
        ).join(
            AcademicClass, Enrollment.class_id == AcademicClass.id
        ).join(
            AcademicYear, Enrollment.academic_year_id == AcademicYear.id
        ).join(
            ExamSchedule, ExamResult.exam_schedule_id == ExamSchedule.id
        ).join(
            Exam, ExamSchedule.exam_id == Exam.id
        ).join(
            Subject, ExamSchedule.subject_id == Subject.id
        ).outerjoin(
            YearlyClassSubject,
            (YearlyClassSubject.subject_id == ExamSchedule.subject_id)
            & (YearlyClassSubject.class_id == Enrollment.class_id)
            & (YearlyClassSubject.academic_year_id == Enrollment.academic_year_id)
            & (YearlyClassSubject.is_deleted == False),  # noqa: E712
        )

        if exam_id:
            stmt = stmt.where(Exam.id == exam_id)
        if academic_year_id:
            stmt = stmt.where(Enrollment.academic_year_id == academic_year_id)
        if class_id:
            stmt = stmt.where(Enrollment.class_id == class_id)

        results = (await session.execute(stmt)).all()

        merit_map: dict[tuple[uuid.UUID, uuid.UUID], dict[str, Any]] = {}
        for row in results:
            key = (row.enrollment_id, row.exam_id)
            if key not in merit_map:
                merit_map[key] = {
                    "enrollment_id": row.enrollment_id,
                    "exam_id": row.exam_id,
                    "exam_name": row.exam_name,
                    "student_name": row.full_name,
                    "student_id_no": row.student_id_no,
                    "roll_number": row.roll_number,
                    "class_id": row.class_id,
                    "class_name": row.class_name,
                    "academic_year_id": row.academic_year_id,
                    "academic_year_name": row.academic_year_name,
                    "total_marks": 0.0,
                    "total_full_marks": 0.0,
                    "total_subjects": 0,
                    "total_grade_points": 0.0,
                    "has_failed": False,
                    "special_status": None,
                    "subjects": {},
                }

            point = grade_to_point.get(row.grade, 0.0) if row.grade else 0.0
            # dict key = subject name → safe against duplicate join rows
            merit_map[key]["subjects"][row.subject_name] = {
                "obtained_marks": row.obtained_marks,
                "full_marks": row.full_marks,
                "grade": row.grade,
                "grade_point": point,
                "affects_result_calculation": row.affects_result_calculation,
            }

            status = row.status.upper() if row.status else "PRESENT"
            affects = (
                row.affects_result_calculation
                if row.affects_result_calculation is not None
                else True
            )

            if affects:
                if status in ("ABSENT", "WITHHELD", "EXPELLED"):
                    if merit_map[key]["special_status"] is None:
                        merit_map[key]["special_status"] = status.capitalize()
                    merit_map[key]["has_failed"] = True
                elif row.grade in failing_grades or row.grade in ("F", "Fail", fail_grade_name):
                    merit_map[key]["has_failed"] = True

        grouped_by_exam_class: dict[tuple[uuid.UUID, uuid.UUID], list[dict]] = {}
        for item in merit_map.values():
            subjects = item["subjects"]
            item["total_marks"] = round(sum(s["obtained_marks"] for s in subjects.values()), 2)
            item["total_full_marks"] = sum(s["full_marks"] for s in subjects.values())
            item["total_subjects"] = len(subjects)
            item["total_grade_points"] = round(
                sum(s["grade_point"] for s in subjects.values()), 4
            )
            item["average_marks"] = round(
                item["total_marks"] / item["total_subjects"]
                if item["total_subjects"] > 0
                else 0.0,
                2,
            )
            item["percentage"] = round(
                (item["total_marks"] / item["total_full_marks"]) * 100
                if item["total_full_marks"] > 0
                else 0.0,
                2,
            )

            # Sort scales descending so the first match is the highest earned grade.
            # Using `percentage >= scale.min_marks` (not `<= max_marks`) avoids
            # the "gap" bug where a decimal like 59.29% falls between integer
            # boundaries (বি max=59, এ- min=60) and matches nothing.
            scales_desc = sorted(scales, key=lambda s: s.min_marks, reverse=True)
            calculated_gpa = 0.0
            calculated_grade = fail_grade_name   # sensible fallback (e.g. "এফ")
            for scale in scales_desc:
                if item["percentage"] >= scale.min_marks:
                    calculated_gpa = scale.grade_point
                    calculated_grade = scale.grade_name
                    break

            if item["has_failed"]:
                item["total_marks"] = 0.0
                item["average_marks"] = 0.0
                item["percentage"] = 0.0
                item["overall_status"] = (
                    item["special_status"] if item["special_status"] else "Fail"
                )
                item["overall_grade"] = fail_grade_name
                item["gpa"] = 0.0
            else:
                item["overall_status"] = "Pass"
                item["overall_grade"] = calculated_grade
                item["gpa"] = round(calculated_gpa, 2)

            group_key = (item["exam_id"], item["class_id"])
            if group_key not in grouped_by_exam_class:
                grouped_by_exam_class[group_key] = []
            grouped_by_exam_class[group_key].append(item)

        final_list: list[dict] = []
        for students in grouped_by_exam_class.values():
            sorted_students = sorted(
                students,
                key=lambda x: (x["has_failed"], -x["total_marks"]),
            )

            rank = 1
            current_rank = 1
            prev_total = None

            for s in sorted_students:
                if s["has_failed"]:
                    s["rank"] = 0
                else:
                    if prev_total is None or abs(s["total_marks"] - prev_total) < 1e-6:
                        s["rank"] = current_rank
                    else:
                        current_rank = rank
                        s["rank"] = current_rank
                    prev_total = s["total_marks"]
                    rank += 1
                final_list.append(s)

        final_list.sort(
            key=lambda x: (
                x["academic_year_name"],
                x["class_name"],
                x["exam_name"],
                x["rank"],
            )
        )
        return final_list
