import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import YearlyClassSubject
from app.models.exam import Exam, ExamResult, ExamSchedule, GradingScale


class ExamService:
    @staticmethod
    async def generate_exam_results(exam_id: uuid.UUID, session: AsyncSession) -> dict:
        """
        For every ExamSchedule of this exam:
          - Find all Enrollments whose class_id matches the schedule's class_id
          - Auto-create any missing ExamResult row (obtained_marks=0, status=PRESENT)
          - Re-calculate grade for all results of those schedules
        This ensures result generation is strictly schedule-based:
        a subject not in any schedule for this exam won't be touched.
        """
        from app.models.student import Enrollment

        # 1. Get all schedules for this exam
        schedules = (
            await session.execute(select(ExamSchedule).where(ExamSchedule.exam_id == exam_id))
        ).scalars().all()
        if not schedules:
            raise HTTPException(status_code=400, detail="No schedules found for this exam")

        schedule_ids = [s.id for s in schedules]
        schedule_map = {s.id: s for s in schedules}

        # 2. For each schedule, find enrolled students in that class and auto-create missing results
        created_count = 0
        for sched in schedules:
            enrollments = (
                await session.execute(
                    select(Enrollment).where(Enrollment.class_id == sched.class_id)
                )
            ).scalars().all()

            for enrollment in enrollments:
                # Check if result already exists for this enrollment + schedule
                existing = (
                    await session.execute(
                        select(ExamResult).where(
                            ExamResult.enrollment_id == enrollment.id,
                            ExamResult.exam_schedule_id == sched.id,
                        )
                    )
                ).scalar_one_or_none()

                if not existing:
                    new_result = ExamResult(
                        enrollment_id=enrollment.id,
                        exam_schedule_id=sched.id,
                        obtained_marks=0.0,
                        grade=None,
                        status="PRESENT",
                        tenant_id=enrollment.tenant_id,
                    )
                    session.add(new_result)
                    created_count += 1

        # Flush so newly created rows are queryable below
        await session.flush()

        # 3. Get grading scales
        scales = (await session.execute(select(GradingScale))).scalars().all()

        # 4. Re-calculate grades for all results belonging to this exam's schedules
        results = (
            await session.execute(
                select(ExamResult).where(ExamResult.exam_schedule_id.in_(schedule_ids))
            )
        ).scalars().all()

        updated_count = 0
        for res in results:
            schedule = schedule_map.get(res.exam_schedule_id)
            if not schedule or schedule.full_marks == 0:
                continue

            status = getattr(res, "status", "PRESENT") or "PRESENT"

            if status != "PRESENT":
                # Absent / Withheld / Expelled — use status string as grade marker
                assigned_grade = status
            else:
                percentage = (res.obtained_marks / schedule.full_marks) * 100
                assigned_grade = None
                for scale in sorted(scales, key=lambda s: s.min_marks, reverse=True):
                    if scale.min_marks <= percentage <= scale.max_marks:
                        assigned_grade = scale.grade_name
                        break

            if assigned_grade and res.grade != assigned_grade:
                res.grade = assigned_grade
                updated_count += 1

        await session.commit()
        return {
            "message": (
                f"Done. Created {created_count} missing result rows, "
                f"updated grades for {updated_count} results."
            )
        }


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
        class_id: uuid.UUID | None = None
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
        failing_grades = {scale.grade_name for scale in scales if hasattr(scale, 'is_pass') and not scale.is_pass}
        
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
            Subject.name.label("subject_name")
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
            (YearlyClassSubject.subject_id == ExamSchedule.subject_id) &
            (YearlyClassSubject.class_id == Enrollment.class_id) &
            (YearlyClassSubject.academic_year_id == Enrollment.academic_year_id)
        )

        if exam_id:
            stmt = stmt.where(Exam.id == exam_id)
        if academic_year_id:
            stmt = stmt.where(Enrollment.academic_year_id == academic_year_id)
        if class_id:
            stmt = stmt.where(Enrollment.class_id == class_id)
            
        results = (await session.execute(stmt)).all()
        
        merit_map = {}
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
                    "subjects": {}
                }
            
            merit_map[key]["total_marks"] += row.obtained_marks
            merit_map[key]["total_full_marks"] += row.full_marks
            merit_map[key]["total_subjects"] += 1
            point = grade_to_point.get(row.grade, 0.0) if row.grade else 0.0
            merit_map[key]["subjects"][row.subject_name] = {
                "obtained_marks": row.obtained_marks,
                "full_marks": row.full_marks,
                "grade": row.grade,
                "grade_point": point
            }
            merit_map[key]["total_grade_points"] += point
            
            status = row.status.upper() if row.status else "PRESENT"
            affects = row.affects_result_calculation if row.affects_result_calculation is not None else True
            
            if affects:
                if status in ("ABSENT", "WITHHELD", "EXPELLED"):
                    if merit_map[key]["special_status"] is None:
                        merit_map[key]["special_status"] = status.capitalize()
                    merit_map[key]["has_failed"] = True
                elif row.grade in failing_grades or row.grade in ("F", "Fail", fail_grade_name):
                    merit_map[key]["has_failed"] = True

        grouped_by_exam_class: dict[tuple[uuid.UUID, uuid.UUID], list[dict]] = {}
        for item in merit_map.values():
            item["average_marks"] = item["total_marks"] / item["total_subjects"] if item["total_subjects"] > 0 else 0.0
            item["percentage"] = (item["total_marks"] / item["total_full_marks"]) * 100 if item["total_full_marks"] > 0 else 0.0
            
            calculated_gpa = 0.0
            calculated_grade = "F"
            for scale in scales:
                if scale.min_marks <= item["percentage"] <= scale.max_marks:
                    calculated_gpa = scale.grade_point
                    calculated_grade = scale.grade_name
                    break
            
            if item["has_failed"]:
                item["total_marks"] = 0.0
                item["average_marks"] = 0.0
                item["percentage"] = 0.0
                item["overall_status"] = item["special_status"] if item["special_status"] else "Fail"
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
            
        final_list = []
        for group_key, students in grouped_by_exam_class.items():
            sorted_students = sorted(
                students,
                key=lambda x: (x["has_failed"], -x["total_marks"])
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
                
        final_list.sort(key=lambda x: (x["academic_year_name"], x["class_name"], x["exam_name"], x["rank"]))
        return final_list
