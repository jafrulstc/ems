import asyncio
import os
import sys

# Add the 'backend' directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.features.auth.models import Role, Permission, RolePermission, User, UserPermissionOverride, UserRole
from app.features.auth.security import hash_password
from app.features.core.models import Organization, Menu, AcademicYear
from app.features.academic.models import Class, Section, Subject, Student, ClassSubject
from app.features.academic.enrollment_models import Enrollment
from app.features.exam.models import ExamType, GradingSystem, GradingRule


async def seed_data():
    async with AsyncSessionLocal() as session:
        # ── 1. Organization (id=1, slug="default") ─────────────────────────────
        result = await session.execute(select(Organization).filter_by(slug="default"))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(id=1, name="Default Organization", slug="default", is_active=True)
            session.add(org)
            await session.commit()
            await session.refresh(org)
        print(f"Organization: id={org.id}, slug={org.slug}")

        # ── 2. Roles ────────────────────────────────────────────────────────────
        roles_data = ["Superadmin", "Admin", "Teacher"]
        role_objs = {}
        for r in roles_data:
            result = await session.execute(select(Role).filter_by(name=r, organization_id=org.id))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(name=r, organization_id=org.id)
                session.add(role)
                await session.flush()
            role_objs[r] = role
        await session.commit()
        print("Roles seeded.")

        # ── 3. Permissions ──────────────────────────────────────────────────────
        permissions_data = [
            # Academic - Classes
            ("academic.classes.view", "View Classes", "Academic", "view"),
            ("academic.classes.create", "Create Classes", "Academic", "create"),
            ("academic.classes.edit", "Edit Classes", "Academic", "edit"),
            ("academic.classes.delete", "Delete Classes", "Academic", "delete"),
            # Academic - Sections
            ("academic.sections.view", "View Sections", "Academic", "view"),
            ("academic.sections.create", "Create Sections", "Academic", "create"),
            ("academic.sections.edit", "Edit Sections", "Academic", "edit"),
            ("academic.sections.delete", "Delete Sections", "Academic", "delete"),
            # Academic - Subjects
            ("academic.subjects.view", "View Subjects", "Academic", "view"),
            ("academic.subjects.create", "Create Subjects", "Academic", "create"),
            ("academic.subjects.edit", "Edit Subjects", "Academic", "edit"),
            ("academic.subjects.delete", "Delete Subjects", "Academic", "delete"),
            # Academic - Class Subjects
            ("academic.class_subjects.view", "View Class Subjects", "Academic", "view"),
            ("academic.class_subjects.create", "Create Class Subjects", "Academic", "create"),
            ("academic.class_subjects.edit", "Edit Class Subjects", "Academic", "edit"),
            ("academic.class_subjects.delete", "Delete Class Subjects", "Academic", "delete"),
            # Academic - Guardians
            ("academic.guardians.view", "View Guardians", "Academic", "view"),
            ("academic.guardians.create", "Create Guardians", "Academic", "create"),
            ("academic.guardians.edit", "Edit Guardians", "Academic", "edit"),
            # Academic - Students
            ("academic.students.view", "View Students", "Academic", "view"),
            ("academic.students.create", "Create Students", "Academic", "create"),
            ("academic.students.edit", "Edit Students", "Academic", "edit"),
            ("academic.students.delete", "Delete Students", "Academic", "delete"),
            # Academic - Enrollments
            ("academic.enrollments.view", "View Enrollments", "Academic", "view"),
            ("academic.enrollments.create", "Create Enrollments", "Academic", "create"),
            ("academic.enrollments.edit", "Edit Enrollments", "Academic", "edit"),
            ("academic.enrollments.delete", "Delete Enrollments", "Academic", "delete"),
            # Exam
            ("exam.exam_types.view", "View Exam Types", "Exam", "view"),
            ("exam.exam_types.create", "Create Exam Types", "Exam", "create"),
            ("exam.exam_types.edit", "Edit Exam Types", "Exam", "edit"),
            ("exam.exam_types.delete", "Delete Exam Types", "Exam", "delete"),
            ("exam.routines.view", "View Routines", "Exam", "view"),
            ("exam.routines.create", "Create Routines", "Exam", "create"),
            ("exam.routines.edit", "Edit Routines", "Exam", "edit"),
            ("exam.marks.view", "View Marks", "Exam", "view"),
            ("exam.marks.entry", "Enter Marks", "Exam", "create"),
            ("exam.grading.view", "View Grading", "Exam", "view"),
            ("exam.grading.create", "Create Grading", "Exam", "create"),
            ("exam.grading.edit", "Edit Grading", "Exam", "edit"),
            ("exam.grading.delete", "Delete Grading", "Exam", "delete"),
            ("exam.results.view", "View Results", "Exam", "view"),
            ("exam.results.create", "Generate Results", "Exam", "create"),
            # Reports
            ("reports.view", "View Reports", "Reports", "view"),
            # Core
            ("core.settings.view", "View Settings", "Core", "view"),
            ("core.users.view", "View Users", "Core", "view"),
            ("core.users.create", "Create Users", "Core", "create"),
            ("core.users.edit", "Edit Users", "Core", "edit"),
            ("core.users.delete", "Delete Users", "Core", "delete"),
            ("core.roles.view", "View Roles", "Core", "view"),
            ("core.roles.create", "Create Roles", "Core", "create"),
            ("core.roles.edit", "Edit Roles", "Core", "edit"),
            ("core.roles.delete", "Delete Roles", "Core", "delete"),
            ("core.academic_years.view", "View Academic Years", "Core", "view"),
            ("core.academic_years.create", "Create Academic Years", "Core", "create"),
            ("core.academic_years.edit", "Edit Academic Years", "Core", "edit"),
            ("core.academic_years.delete", "Delete Academic Years", "Core", "delete"),
        ]

        perm_objs = {}
        for key, label, module, action in permissions_data:
            result = await session.execute(select(Permission).filter_by(key=key))
            perm = result.scalar_one_or_none()
            if not perm:
                perm = Permission(key=key, label=label, module=module, action=action)
                session.add(perm)
                await session.flush()
            perm_objs[key] = perm
        await session.commit()
        print(f"Permissions seeded: {len(perm_objs)} total.")

        # ── 4. Role-Permissions ─────────────────────────────────────────────────
        admin_perms = list(perm_objs.values())
        teacher_perms = [
            perm_objs["academic.classes.view"],
            perm_objs["academic.sections.view"],
            perm_objs["academic.subjects.view"],
            perm_objs["academic.class_subjects.view"],
            perm_objs["academic.students.view"],
            perm_objs["academic.guardians.view"],
            perm_objs["academic.enrollments.view"],
            perm_objs["exam.exam_types.view"],
            perm_objs["exam.routines.view"],
            perm_objs["exam.marks.view"],
            perm_objs["exam.marks.entry"],
            perm_objs["exam.grading.view"],
            perm_objs["exam.results.view"],
            perm_objs["reports.view"],
        ]

        for p in admin_perms:
            result = await session.execute(select(RolePermission).filter_by(role_id=role_objs["Admin"].id, permission_id=p.id))
            if not result.scalar_one_or_none():
                session.add(RolePermission(role_id=role_objs["Admin"].id, permission_id=p.id))

        for p in teacher_perms:
            result = await session.execute(select(RolePermission).filter_by(role_id=role_objs["Teacher"].id, permission_id=p.id))
            if not result.scalar_one_or_none():
                session.add(RolePermission(role_id=role_objs["Teacher"].id, permission_id=p.id))

        await session.commit()
        print("Role-Permissions seeded.")

        # ── 5. Users ────────────────────────────────────────────────────────────
        users_data = [
            ("admin@ems.local", "Admin User", True, [role_objs["Superadmin"]]),
            ("teacher@ems.local", "Teacher User", False, [role_objs["Teacher"]]),
        ]

        user_objs = {}
        for email, name, is_super, roles in users_data:
            result = await session.execute(select(User).filter_by(email=email, organization_id=org.id))
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    email=email,
                    hashed_password=hash_password("password123"),
                    full_name=name,
                    is_active=True,
                    is_superuser=is_super,
                    organization_id=org.id
                )
                session.add(user)
                await session.flush()
            for r in roles:
                result = await session.execute(select(UserRole).filter_by(user_id=user.id, role_id=r.id))
                if not result.scalar_one_or_none():
                    session.add(UserRole(user_id=user.id, role_id=r.id))
            user_objs[email] = user
        await session.commit()
        print("Users seeded. (Password: password123)")

        # ── 6. Permission Override ──────────────────────────────────────────────
        teacher_user = user_objs["teacher@ems.local"]
        perm_to_override = perm_objs["exam.marks.entry"]
        result = await session.execute(select(UserPermissionOverride).filter_by(user_id=teacher_user.id, permission_id=perm_to_override.id))
        if not result.scalar_one_or_none():
            session.add(UserPermissionOverride(
                user_id=teacher_user.id,
                permission_id=perm_to_override.id,
                is_granted=False,
                organization_id=org.id
            ))
            await session.commit()
            print(f"Override: {teacher_user.email} → exam.marks.entry = False")

        # ── 7. Menus ────────────────────────────────────────────────────────────
        menus_data = [
            (None, "Dashboard", "pi pi-home", "home", None, 10),
            (None, "Academic", "pi pi-book", None, None, 20),
            (None, "Exam", "pi pi-chart-bar", None, None, 30),
            (None, "Reports", "pi pi-file", None, "reports.view", 40),
            (None, "Settings", "pi pi-cog", None, "core.settings.view", 100),
        ]

        menu_objs = {}
        for parent_label, label, icon, route, perm_key, order in menus_data:
            parent_id = menu_objs[parent_label].id if parent_label else None
            result = await session.execute(
                select(Menu).filter_by(organization_id=org.id, label=label, parent_id=parent_id)
            )
            menu = result.scalar_one_or_none()
            if not menu:
                menu = Menu(
                    organization_id=org.id, parent_id=parent_id, label=label,
                    icon=icon, route_name=route, permission_key=perm_key,
                    order=order, is_active=True
                )
                session.add(menu)
                await session.flush()
            menu_objs[label] = menu

        child_menus = [
            ("Academic", "Classes", None, "academic.classes", "academic.classes.view", 1),
            ("Academic", "Sections", None, "academic.sections", "academic.sections.view", 2),
            ("Academic", "Subjects", None, "academic.subjects", "academic.subjects.view", 3),
            ("Academic", "Class Subjects", None, "academic.class-subjects", "academic.class_subjects.view", 4),
            ("Academic", "Guardians", None, "academic.guardians", "academic.guardians.view", 5),
            ("Academic", "Students", None, "academic.students", "academic.students.view", 6),
            ("Academic", "Enrollments", None, "academic.enrollments", "academic.enrollments.view", 7),
            ("Exam", "Exam Config", None, "exam.types", "exam.exam_types.view", 1),
            ("Exam", "Routines", None, "exam.routines", "exam.routines.view", 2),
            ("Exam", "Marks Entry", None, "exam.marks", "exam.marks.entry", 3),
            ("Exam", "Results", None, "exam.results", "exam.results.view", 4),
            ("Reports", "Academic Reports", None, "reports.academic", "reports.view", 1),
            ("Reports", "Exam Reports", None, "reports.exam", "reports.view", 2),
        ]

        for parent_label, label, icon, route, perm_key, order in child_menus:
            parent_id = menu_objs[parent_label].id
            result = await session.execute(
                select(Menu).filter_by(organization_id=org.id, label=label, parent_id=parent_id)
            )
            menu = result.scalar_one_or_none()
            if not menu:
                menu = Menu(
                    organization_id=org.id, parent_id=parent_id, label=label,
                    icon=icon, route_name=route, permission_key=perm_key,
                    order=order, is_active=True
                )
                session.add(menu)
                await session.flush()
            menu_objs[label] = menu
        await session.commit()
        print("Menus seeded.")

        # ── 8. Academic Year ────────────────────────────────────────────────────
        result = await session.execute(select(AcademicYear).filter_by(organization_id=org.id))
        ay = result.scalar_one_or_none()
        if not ay:
            ay = AcademicYear(
                name="2025", start_date="2025-01-01", end_date="2025-12-31",
                is_active=True, organization_id=org.id
            )
            session.add(ay)
            await session.flush()
            await session.commit()
            print(f"Academic Year: id={ay.id}, name={ay.name}")

        # ── 9. Sample Classes ───────────────────────────────────────────────────
        classes_data = [
            ("Class 1", "প্রথম শ্রেণি", 1),
            ("Class 2", "দ্বিতীয় শ্রেণি", 2),
            ("Class 3", "তৃতীয় শ্রেণি", 3),
            ("Class 4", "চতুর্থ শ্রেণি", 4),
            ("Class 5", "পঞ্চম শ্রেণি", 5),
        ]
        class_objs = {}
        for name, name_bn, level in classes_data:
            result = await session.execute(select(Class).filter_by(name=name, organization_id=org.id))
            cls = result.scalar_one_or_none()
            if not cls:
                cls = Class(name=name, name_bn=name_bn, numeric_level=level, is_active=True, organization_id=org.id)
                session.add(cls)
                await session.flush()
            class_objs[name] = cls
        await session.commit()
        print(f"Classes seeded: {len(class_objs)} total.")

        # ── 10. Sample Sections ─────────────────────────────────────────────────
        sections_data = [
            ("Class 1", "A", "ক"),
            ("Class 1", "B", "খ"),
            ("Class 2", "A", "ক"),
            ("Class 3", "A", "ক"),
            ("Class 4", "A", "ক"),
            ("Class 5", "A", "ক"),
        ]
        section_objs = {}
        for cls_name, sec_name, sec_name_bn in sections_data:
            result = await session.execute(
                select(Section).filter_by(name=sec_name, class_id=class_objs[cls_name].id, organization_id=org.id)
            )
            sec = result.scalar_one_or_none()
            if not sec:
                sec = Section(name=sec_name, name_bn=sec_name_bn, class_id=class_objs[cls_name].id, organization_id=org.id)
                session.add(sec)
                await session.flush()
            section_objs[f"{cls_name}-{sec_name}"] = sec
        await session.commit()
        print(f"Sections seeded: {len(section_objs)} total.")

        # ── 11. Sample Subjects ─────────────────────────────────────────────────
        subjects_data = [
            ("Bangla", "বাংলা", "BAN", False),
            ("English", "ইংরেজি", "ENG", False),
            ("Mathematics", "গণিত", "MAT", False),
            ("Science", "বিজ্ঞান", "SCI", False),
            ("Social Science", "সমাজবিজ্ঞান", "SOC", False),
            ("Religion", "ধর্ম", "REL", False),
            ("ICT", "তথ্য ও যোগাযোগ প্রযুক্তি", "ICT", False),
            ("Physical Education", "শারীরিক শিক্ষা", "PE", True),
            ("Art", "চারুকলা", "ART", True),
        ]
        subject_objs = {}
        for name, name_bn, code, optional in subjects_data:
            result = await session.execute(select(Subject).filter_by(name=name, organization_id=org.id))
            sub = result.scalar_one_or_none()
            if not sub:
                sub = Subject(name=name, name_bn=name_bn, code=code, is_optional=optional, organization_id=org.id)
                session.add(sub)
                await session.flush()
            subject_objs[name] = sub
        await session.commit()
        print(f"Subjects seeded: {len(subject_objs)} total.")

        # ── 12. Class-Subject Mappings ──────────────────────────────────────────
        mapping_data = [
            # Class 1: Bangla, English, Math
            ("Class 1", "Bangla", 100, 33),
            ("Class 1", "English", 100, 33),
            ("Class 1", "Mathematics", 100, 33),
            # Class 2: + Science
            ("Class 2", "Bangla", 100, 33),
            ("Class 2", "English", 100, 33),
            ("Class 2", "Mathematics", 100, 33),
            ("Class 2", "Science", 100, 33),
            # Class 3-5: all mandatory + some optional
            ("Class 3", "Bangla", 100, 33),
            ("Class 3", "English", 100, 33),
            ("Class 3", "Mathematics", 100, 33),
            ("Class 3", "Science", 100, 33),
            ("Class 3", "Social Science", 100, 33),
            ("Class 4", "Bangla", 100, 33),
            ("Class 4", "English", 100, 33),
            ("Class 4", "Mathematics", 100, 33),
            ("Class 4", "Science", 100, 33),
            ("Class 4", "Social Science", 100, 33),
            ("Class 4", "Religion", 100, 33),
            ("Class 5", "Bangla", 100, 33),
            ("Class 5", "English", 100, 33),
            ("Class 5", "Mathematics", 100, 33),
            ("Class 5", "Science", 100, 33),
            ("Class 5", "Social Science", 100, 33),
            ("Class 5", "Religion", 100, 33),
            ("Class 5", "ICT", 100, 33),
        ]
        for cls_name, sub_name, full, passing in mapping_data:
            result = await session.execute(
                select(ClassSubject).filter_by(
                    class_id=class_objs[cls_name].id,
                    subject_id=subject_objs[sub_name].id,
                    organization_id=org.id
                )
            )
            cs = result.scalar_one_or_none()
            if not cs:
                cs = ClassSubject(
                    class_id=class_objs[cls_name].id,
                    subject_id=subject_objs[sub_name].id,
                    full_marks=full, pass_marks=passing,
                    organization_id=org.id
                )
                session.add(cs)
        await session.commit()
        print("Class-Subject mappings seeded.")

        # ── 13. Sample Students ─────────────────────────────────────────────────
        students_data = [
            ("STU-001", "Rahim Uddin", "Male", "2016-03-15"),
            ("STU-002", "Karim Hossain", "Male", "2016-07-22"),
            ("STU-003", "Fatima Begum", "Female", "2016-01-10"),
            ("STU-004", "Amina Khatun", "Female", "2015-11-05"),
            ("STU-005", "Jamal Ahmed", "Male", "2015-06-18"),
            ("STU-006", "Nasima Akter", "Female", "2016-09-01"),
            ("STU-007", "Habib Molla", "Male", "2014-12-20"),
            ("STU-008", "Salma Parvin", "Female", "2014-04-12"),
            ("STU-009", "Arif Rahman", "Male", "2014-08-30"),
            ("STU-010", "Nargis Sultana", "Female", "2013-02-14"),
        ]
        student_objs = {}
        for reg, name, gender, dob in students_data:
            result = await session.execute(select(Student).filter_by(registration_no=reg, organization_id=org.id))
            stu = result.scalar_one_or_none()
            if not stu:
                stu = Student(
                    registration_no=reg, full_name=name, gender=gender,
                    dob=dob, is_active=True, organization_id=org.id
                )
                session.add(stu)
                await session.flush()
            student_objs[reg] = stu
        await session.commit()
        print(f"Students seeded: {len(student_objs)} total.")

        # ── 14. Sample Enrollments ──────────────────────────────────────────────
        enrollments_data = [
            ("STU-001", "Class 1-A", 1),
            ("STU-002", "Class 1-A", 2),
            ("STU-003", "Class 1-B", 1),
            ("STU-004", "Class 2-A", 1),
            ("STU-005", "Class 3-A", 1),
            ("STU-006", "Class 1-B", 2),
            ("STU-007", "Class 4-A", 1),
            ("STU-008", "Class 5-A", 1),
            ("STU-009", "Class 4-A", 2),
            ("STU-010", "Class 5-A", 2),
        ]
        for reg, sec_key, roll in enrollments_data:
            if sec_key not in section_objs:
                continue
            result = await session.execute(
                select(Enrollment).filter_by(
                    student_id=student_objs[reg].id,
                    section_id=section_objs[sec_key].id,
                    academic_year_id=ay.id,
                    organization_id=org.id
                )
            )
            enr = result.scalar_one_or_none()
            if not enr:
                enr = Enrollment(
                    student_id=student_objs[reg].id,
                    section_id=section_objs[sec_key].id,
                    academic_year_id=ay.id,
                    roll_no=str(roll),
                    is_active=True,
                    organization_id=org.id
                )
                session.add(enr)
        await session.commit()
        print("Enrollments seeded.")

        # ── 15. Exam Types ──────────────────────────────────────────────────────
        exam_types_data = [
            ("Midterm", "মাঝামাঝি পরীক্ষা", "Mid-term examination"),
            ("Final", "চূড়ান্ত পরীক্ষা", "Final examination"),
            ("Unit Test", "ইউনিট পরীক্ষা", "Periodic unit test"),
        ]
        et_objs = {}
        for name, name_bn, desc in exam_types_data:
            result = await session.execute(select(ExamType).filter_by(name=name, organization_id=org.id))
            et = result.scalar_one_or_none()
            if not et:
                et = ExamType(name=name, name_bn=name_bn, description=desc, organization_id=org.id)
                session.add(et)
                await session.flush()
            et_objs[name] = et
        await session.commit()
        print(f"Exam Types seeded: {len(et_objs)} total.")

        # ── 16. Grading System ──────────────────────────────────────────────────
        result = await session.execute(select(GradingSystem).filter_by(name="GPA 5.0", organization_id=org.id))
        gs = result.scalar_one_or_none()
        if not gs:
            gs = GradingSystem(name="GPA 5.0", is_default=True, organization_id=org.id)
            session.add(gs)
            await session.flush()

            rules = [
                (80, 100, "A+", 5.00, "Outstanding"),
                (70, 79, "A", 4.00, "Excellent"),
                (60, 69, "A-", 3.50, "Very Good"),
                (50, 59, "B", 3.00, "Good"),
                (40, 49, "C", 2.00, "Average"),
                (33, 39, "D", 1.00, "Below Average"),
                (0, 32, "F", 0.00, "Fail"),
            ]
            for mn, mx, grade, point, remark in rules:
                session.add(GradingRule(
                    grading_system_id=gs.id, min_marks=mn, max_marks=mx,
                    grade=grade, grade_point=point, remarks=remark,
                    organization_id=org.id
                ))
            await session.commit()
            print("Grading System 'GPA 5.0' seeded with rules.")

        print("\n✅ Seed data complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())
