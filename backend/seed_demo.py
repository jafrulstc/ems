import asyncio
import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.session import engine
from app.models.academic import (
    AcademicClass,
    AcademicYear,
    Department,
    Section,
    Subject,
    YearlyClassSubject,
)
from app.models.exam import Exam, ExamResult, ExamSchedule, GradingScale
from app.models.student import Enrollment, Guardian, Student

# Import all models
from app.models.tenant import Branch, Institute

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_test_institute():
    async with AsyncSessionLocal() as session:
        # Find institute
        stmt = select(Institute).where(Institute.slug.like("%test%"))
        result = await session.execute(stmt)
        institute = result.scalars().first()
        
        if not institute:
            stmt = select(Institute).where(Institute.slug == "tahzibul-ummah")
            result = await session.execute(stmt)
            institute = result.scalars().first()

        if not institute:
            print("No test institute found!")
            return

        tenant_id = institute.id
        print(f"Seeding data for Institute: {institute.name} ({tenant_id})")

        # Create Branch
        branch = Branch(name="Main Branch", tenant_id=tenant_id)
        session.add(branch)
        await session.flush()

        # Academic Year
        academic_year = AcademicYear(name="2026", start_date=datetime.date(2026, 1, 1), end_date=datetime.date(2026, 12, 31), tenant_id=tenant_id)
        session.add(academic_year)
        await session.flush()

        # Department
        dept = Department(name="Science", level="SSC", tenant_id=tenant_id)
        session.add(dept)
        await session.flush()

        # Class
        ac_class = AcademicClass(name="Class 10", level="SSC", department_id=dept.id, tenant_id=tenant_id)
        session.add(ac_class)
        await session.flush()

        # Section
        section = Section(name="A", class_id=ac_class.id, branch_id=branch.id, tenant_id=tenant_id)
        session.add(section)
        await session.flush()

        # Subjects
        subj_math = Subject(name="Mathematics", code="MATH101", tenant_id=tenant_id)
        subj_eng = Subject(name="English", code="ENG101", tenant_id=tenant_id)
        session.add_all([subj_math, subj_eng])
        await session.flush()

        # Yearly Class Subjects
        ycs_math = YearlyClassSubject(academic_year_id=academic_year.id, class_id=ac_class.id, subject_id=subj_math.id, tenant_id=tenant_id)
        ycs_eng = YearlyClassSubject(academic_year_id=academic_year.id, class_id=ac_class.id, subject_id=subj_eng.id, tenant_id=tenant_id)
        session.add_all([ycs_math, ycs_eng])
        await session.flush()

        # Guardians
        g1 = Guardian(name="Abdur Rahman", phone="01711000001", tenant_id=tenant_id)
        g2 = Guardian(name="Mofizur Rahman", phone="01711000002", tenant_id=tenant_id)
        session.add_all([g1, g2])
        await session.flush()

        # Students
        s1 = Student(first_name="Rahim", last_name="Miah", gender="Male", date_of_birth=datetime.date(2010, 5, 12), guardian_id=g1.id, branch_id=branch.id, tenant_id=tenant_id)
        s2 = Student(first_name="Karim", last_name="Hossain", gender="Male", date_of_birth=datetime.date(2010, 8, 22), guardian_id=g1.id, branch_id=branch.id, tenant_id=tenant_id)
        s3 = Student(first_name="Salma", last_name="Khatun", gender="Female", date_of_birth=datetime.date(2011, 2, 10), guardian_id=g2.id, branch_id=branch.id, tenant_id=tenant_id)
        session.add_all([s1, s2, s3])
        await session.flush()

        # Enrollments
        today = datetime.date.today()
        e1 = Enrollment(student_id=s1.id, academic_year_id=academic_year.id, class_id=ac_class.id, section_id=section.id, enrollment_number="ENR-001", roll_number="1", enrollment_date=today, tenant_id=tenant_id)
        e2 = Enrollment(student_id=s2.id, academic_year_id=academic_year.id, class_id=ac_class.id, section_id=section.id, enrollment_number="ENR-002", roll_number="2", enrollment_date=today, tenant_id=tenant_id)
        e3 = Enrollment(student_id=s3.id, academic_year_id=academic_year.id, class_id=ac_class.id, section_id=section.id, enrollment_number="ENR-003", roll_number="3", enrollment_date=today, tenant_id=tenant_id)
        session.add_all([e1, e2, e3])
        await session.flush()

        # Grading Scales
        gs_a = GradingScale(grade_name="A", min_marks=80, max_marks=100, grade_point=5.0, is_pass=True, tenant_id=tenant_id)
        gs_b = GradingScale(grade_name="B", min_marks=60, max_marks=79.99, grade_point=4.0, is_pass=True, tenant_id=tenant_id)
        gs_c = GradingScale(grade_name="C", min_marks=40, max_marks=59.99, grade_point=3.0, is_pass=True, tenant_id=tenant_id)
        gs_f = GradingScale(grade_name="F", min_marks=0, max_marks=39.99, grade_point=0.0, is_pass=False, tenant_id=tenant_id)
        session.add_all([gs_a, gs_b, gs_c, gs_f])
        await session.flush()

        # Exam
        exam = Exam(name="Mid Term Examination", start_date=datetime.date(2026, 6, 1), end_date=datetime.date(2026, 6, 10), academic_year_id=academic_year.id, max_failing_subjects=0, tenant_id=tenant_id)
        session.add(exam)
        await session.flush()

        # Exam Schedules
        es_math = ExamSchedule(exam_id=exam.id, subject_id=subj_math.id, exam_date=datetime.date(2026, 6, 2), start_time=datetime.time(10, 0), end_time=datetime.time(13, 0), full_marks=100, pass_marks=40, tenant_id=tenant_id)
        es_eng = ExamSchedule(exam_id=exam.id, subject_id=subj_eng.id, exam_date=datetime.date(2026, 6, 4), start_time=datetime.time(10, 0), end_time=datetime.time(13, 0), full_marks=100, pass_marks=40, tenant_id=tenant_id)
        session.add_all([es_math, es_eng])
        await session.flush()

        # Exam Results (Marks Entry)
        # Rahim - Passed both
        er1 = ExamResult(enrollment_id=e1.id, exam_schedule_id=es_math.id, obtained_marks=85, grade="A", tenant_id=tenant_id)
        er2 = ExamResult(enrollment_id=e1.id, exam_schedule_id=es_eng.id, obtained_marks=75, grade="B", tenant_id=tenant_id)
        
        # Karim - Failed English
        er3 = ExamResult(enrollment_id=e2.id, exam_schedule_id=es_math.id, obtained_marks=65, grade="B", tenant_id=tenant_id)
        er4 = ExamResult(enrollment_id=e2.id, exam_schedule_id=es_eng.id, obtained_marks=35, grade="F", tenant_id=tenant_id)
        
        # Salma - Failed Both
        er5 = ExamResult(enrollment_id=e3.id, exam_schedule_id=es_math.id, obtained_marks=30, grade="F", tenant_id=tenant_id)
        er6 = ExamResult(enrollment_id=e3.id, exam_schedule_id=es_eng.id, obtained_marks=25, grade="F", tenant_id=tenant_id)

        session.add_all([er1, er2, er3, er4, er5, er6])
        
        await session.commit()
        print("Demo data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_test_institute())
