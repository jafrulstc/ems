import asyncio
import datetime
import random
import string
from sqlalchemy import select, delete
from app.db.session import engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.tenant import Institute, Branch
from app.models.academic import AcademicYear, Department, AcademicClass, Section, Subject
from app.models.student import Student, Guardian, Enrollment
from app.models.exam import Exam, ExamSchedule, ExamResult, GradingScale

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

first_names = ["Rahim", "Karim", "Salma", "Sadia", "Rifat", "Hasan", "Sumaiya", "Rakib", "Arif", "Fatema", "Tarek", "Sajid", "Mim", "Nadia", "Sohan", "Sakib", "Tania", "Asif", "Mehedi", "Aisha", "Omar", "Khadija", "Yusuf", "Zainab", "Ali", "Mary", "Imran", "Farhana", "Tushar", "Nusrat"]
last_names = ["Miah", "Hossain", "Khatun", "Akter", "Rahman", "Islam", "Uddin", "Ahmed", "Chowdhury", "Khan", "Haque", "Ali", "Das", "Sikder", "Molla"]

async def clear_existing_data(session, tenant_id):
    await session.execute(delete(ExamResult).where(ExamResult.tenant_id == tenant_id))
    await session.execute(delete(ExamSchedule).where(ExamSchedule.tenant_id == tenant_id))
    await session.execute(delete(Exam).where(Exam.tenant_id == tenant_id))
    await session.execute(delete(Enrollment).where(Enrollment.tenant_id == tenant_id))
    await session.execute(delete(Student).where(Student.tenant_id == tenant_id))
    await session.execute(delete(Guardian).where(Guardian.tenant_id == tenant_id))
    await session.execute(delete(Subject).where(Subject.tenant_id == tenant_id))
    await session.execute(delete(Section).where(Section.tenant_id == tenant_id))
    await session.execute(delete(AcademicClass).where(AcademicClass.tenant_id == tenant_id))
    await session.execute(delete(Department).where(Department.tenant_id == tenant_id))
    await session.execute(delete(AcademicYear).where(AcademicYear.tenant_id == tenant_id))
    await session.execute(delete(GradingScale).where(GradingScale.tenant_id == tenant_id))
    await session.flush()

def get_grade(marks):
    if marks >= 80: return "A+"
    if marks >= 70: return "A"
    if marks >= 60: return "A-"
    if marks >= 50: return "B"
    if marks >= 40: return "C"
    if marks >= 33: return "D"
    return "F"

async def seed_large_demo():
    async with AsyncSessionLocal() as session:
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
        print(f"Generating large demo data for Institute: {institute.name}")
        
        await clear_existing_data(session, tenant_id)
        
        stmt = select(Branch).where(Branch.tenant_id == tenant_id)
        result = await session.execute(stmt)
        branch = result.scalars().first()
        if not branch:
            branch = Branch(name="Main Branch", tenant_id=tenant_id)
            session.add(branch)
            await session.flush()

        academic_year = AcademicYear(name="2026", start_date=datetime.date(2026, 1, 1), end_date=datetime.date(2026, 12, 31), tenant_id=tenant_id)
        session.add(academic_year)
        
        dept = Department(name="General", level="Primary", tenant_id=tenant_id)
        session.add(dept)
        await session.flush()

        # Grading Scales (Standard Bangladesh Primary)
        scales = [
            ("A+", 80, 100, 5.0, True),
            ("A", 70, 79.99, 4.0, True),
            ("A-", 60, 69.99, 3.5, True),
            ("B", 50, 59.99, 3.0, True),
            ("C", 40, 49.99, 2.0, True),
            ("D", 33, 39.99, 1.0, True),
            ("F", 0, 32.99, 0.0, False)
        ]
        for name, min_m, max_m, gp, is_pass in scales:
            session.add(GradingScale(grade_name=name, min_marks=min_m, max_marks=max_m, grade_point=gp, is_pass=is_pass, tenant_id=tenant_id))

        exam = Exam(name="Annual Examination 2026", start_date=datetime.date(2026, 11, 20), end_date=datetime.date(2026, 11, 30), academic_year_id=academic_year.id, max_failing_subjects=0, tenant_id=tenant_id)
        session.add(exam)
        await session.flush()

        today = datetime.date.today()
        guardians = []
        for _ in range(50):
            g = Guardian(name=random.choice(first_names) + " " + random.choice(last_names), phone="017" + "".join(random.choices(string.digits, k=8)), tenant_id=tenant_id)
            session.add(g)
            guardians.append(g)
        await session.flush()

        global_enrollment_counter = 1000
        classes_data = [("Class 1", "Primary"), ("Class 2", "Primary"), ("Class 3", "Primary"), ("Class 4", "Primary"), ("Class 5", "Primary")]
        
        for cls_name, lvl in classes_data:
            ac_class = AcademicClass(name=cls_name, level=lvl, department_id=dept.id, tenant_id=tenant_id)
            session.add(ac_class)
            await session.flush()
            
            section = Section(name="A", class_id=ac_class.id, branch_id=branch.id, tenant_id=tenant_id)
            session.add(section)
            await session.flush()

            subj_bangla = Subject(name="Bangla", code=f"BAN-{cls_name.split()[1]}", class_id=ac_class.id, tenant_id=tenant_id)
            subj_english = Subject(name="English", code=f"ENG-{cls_name.split()[1]}", class_id=ac_class.id, tenant_id=tenant_id)
            subj_math = Subject(name="Mathematics", code=f"MAT-{cls_name.split()[1]}", class_id=ac_class.id, tenant_id=tenant_id)
            session.add_all([subj_bangla, subj_english, subj_math])
            await session.flush()

            sch_ban = ExamSchedule(exam_id=exam.id, subject_id=subj_bangla.id, exam_date=datetime.date(2026, 11, 21), start_time=datetime.time(10, 0), end_time=datetime.time(13, 0), full_marks=100, pass_marks=33, tenant_id=tenant_id)
            sch_eng = ExamSchedule(exam_id=exam.id, subject_id=subj_english.id, exam_date=datetime.date(2026, 11, 23), start_time=datetime.time(10, 0), end_time=datetime.time(13, 0), full_marks=100, pass_marks=33, tenant_id=tenant_id)
            sch_mat = ExamSchedule(exam_id=exam.id, subject_id=subj_math.id, exam_date=datetime.date(2026, 11, 25), start_time=datetime.time(10, 0), end_time=datetime.time(13, 0), full_marks=100, pass_marks=33, tenant_id=tenant_id)
            session.add_all([sch_ban, sch_eng, sch_mat])
            await session.flush()

            num_students = random.randint(18, 24)
            for roll in range(1, num_students + 1):
                gender = random.choice(["Male", "Female"])
                stu = Student(
                    first_name=random.choice(first_names),
                    last_name=random.choice(last_names),
                    gender=gender,
                    date_of_birth=datetime.date(2015 - int(cls_name.split()[1]), random.randint(1, 12), random.randint(1, 28)),
                    guardian_id=random.choice(guardians).id,
                    branch_id=branch.id,
                    tenant_id=tenant_id
                )
                session.add(stu)
                await session.flush()

                enr = Enrollment(
                    student_id=stu.id,
                    academic_year_id=academic_year.id,
                    class_id=ac_class.id,
                    section_id=section.id,
                    enrollment_number=f"ENR-{global_enrollment_counter}",
                    roll_number=str(roll),
                    enrollment_date=today,
                    tenant_id=tenant_id
                )
                session.add(enr)
                global_enrollment_counter += 1
                await session.flush()

                # Generate random marks
                base_competency = random.randint(30, 95)
                for sch in [sch_ban, sch_eng, sch_mat]:
                    obtained = max(0, min(100, int(random.gauss(base_competency, 15))))
                    grade = get_grade(obtained)
                    session.add(ExamResult(enrollment_id=enr.id, exam_schedule_id=sch.id, obtained_marks=obtained, grade=grade, tenant_id=tenant_id))

        await session.commit()
        print("Large demo data successfully generated!")

if __name__ == "__main__":
    asyncio.run(seed_large_demo())
