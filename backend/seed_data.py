import asyncio
import os
import sys

# Add the 'backend' directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.features.auth.models import Role, Permission, RolePermission, User, UserPermissionOverride, UserRole
from app.features.auth.security import hash_password
from app.features.core.models import Organization, Menu

async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Create a Default Organization if it doesn't exist
        result = await session.execute(select(Organization).filter_by(slug="default"))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(name="Default Organization", slug="default", is_active=True)
            session.add(org)
            await session.commit()
            await session.refresh(org)
        print(f"Organization ID: {org.id}")

        # 2. Roles
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

        # 3. Permissions
        permissions_data = [
            # Academic
            ("academic.classes.view", "View Classes", "Academic", "view"),
            ("academic.classes.create", "Create Classes", "Academic", "create"),
            ("academic.classes.edit", "Edit Classes", "Academic", "edit"),
            ("academic.classes.delete", "Delete Classes", "Academic", "delete"),
            ("academic.sections.view", "View Sections", "Academic", "view"),
            ("academic.sections.create", "Create Sections", "Academic", "create"),
            ("academic.sections.edit", "Edit Sections", "Academic", "edit"),
            ("academic.sections.delete", "Delete Sections", "Academic", "delete"),
            ("academic.subjects.view", "View Subjects", "Academic", "view"),
            ("academic.subjects.create", "Create Subjects", "Academic", "create"),
            ("academic.subjects.edit", "Edit Subjects", "Academic", "edit"),
            ("academic.subjects.delete", "Delete Subjects", "Academic", "delete"),
            ("academic.guardians.view", "View Guardians", "Academic", "view"),
            ("academic.guardians.create", "Create Guardians", "Academic", "create"),
            ("academic.guardians.edit", "Edit Guardians", "Academic", "edit"),
            ("academic.students.view", "View Students", "Academic", "view"),
            ("academic.students.create", "Create Students", "Academic", "create"),
            ("academic.students.edit", "Edit Students", "Academic", "edit"),
            ("academic.students.delete", "Delete Students", "Academic", "delete"),
            # Exam
            ("exam.marks.view", "View Marks", "Exam", "view"),
            ("exam.marks.entry", "Enter Marks", "Exam", "create"),
            # Reports
            ("reports.view", "View Reports", "Reports", "view"),
            # Core
            ("core.settings.view", "View Settings", "Core", "view"),
            ("core.users.view", "View Users", "Core", "view"),
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
        print("Permissions seeded.")

        # 4. Role-Permissions
        admin_perms = list(perm_objs.values())
        teacher_perms = [
            perm_objs["academic.classes.view"],
            perm_objs["academic.sections.view"],
            perm_objs["academic.subjects.view"],
            perm_objs["academic.students.view"],
            perm_objs["exam.marks.view"],
            perm_objs["exam.marks.entry"],
        ]

        # Assign Admin
        for p in admin_perms:
            result = await session.execute(select(RolePermission).filter_by(role_id=role_objs["Admin"].id, permission_id=p.id))
            if not result.scalar_one_or_none():
                session.add(RolePermission(role_id=role_objs["Admin"].id, permission_id=p.id))
        
        # Assign Teacher
        for p in teacher_perms:
            result = await session.execute(select(RolePermission).filter_by(role_id=role_objs["Teacher"].id, permission_id=p.id))
            if not result.scalar_one_or_none():
                session.add(RolePermission(role_id=role_objs["Teacher"].id, permission_id=p.id))
        
        await session.commit()
        print("Role-Permissions seeded.")

        # 5. Users
        users_data = [
            ("admin@ems.local", "Superadmin User", True, [role_objs["Superadmin"]]), # is_superuser=True
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
            
            # assign roles explicitly using UserRole
            for r in roles:
                result = await session.execute(select(UserRole).filter_by(user_id=user.id, role_id=r.id))
                if not result.scalar_one_or_none():
                    session.add(UserRole(user_id=user.id, role_id=r.id))
            
            user_objs[email] = user
        await session.commit()
        print("Users seeded. (Password: password123)")

        # 6. Override
        # Let's give teacher@ems.local explicitly FALSE for 'exam.marks.entry' as an override test
        teacher_user = user_objs["teacher@ems.local"]
        perm_to_override = perm_objs["exam.marks.entry"]
        result = await session.execute(select(UserPermissionOverride).filter_by(user_id=teacher_user.id, permission_id=perm_to_override.id))
        override = result.scalar_one_or_none()
        if not override:
            override = UserPermissionOverride(
                user_id=teacher_user.id,
                permission_id=perm_to_override.id,
                is_granted=False,
                organization_id=org.id
            )
            session.add(override)
            await session.commit()
            print(f"Override seeded for {teacher_user.email}: exam.marks.entry = False")

        # 7. Menus
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
                    organization_id=org.id,
                    parent_id=parent_id,
                    label=label,
                    icon=icon,
                    route_name=route,
                    permission_key=perm_key,
                    order=order,
                    is_active=True
                )
                session.add(menu)
                await session.flush()
            menu_objs[label] = menu
        
        # Child menus
        child_menus = [
            ("Academic", "Classes", None, "academic.classes", "academic.classes.view", 1),
            ("Academic", "Sections", None, "academic.sections", "academic.sections.view", 2),
            ("Academic", "Subjects", None, "academic.subjects", "academic.subjects.view", 3),
            ("Academic", "Guardians", None, "academic.guardians", "academic.guardians.view", 4),
            ("Academic", "Students", None, "academic.students", "academic.students.view", 5),
            ("Exam", "Marks Entry", None, "exam.marks", "exam.marks.entry", 1),
            ("Exam", "Results", None, "exam.results", "exam.marks.view", 2),
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
                    organization_id=org.id,
                    parent_id=parent_id,
                    label=label,
                    icon=icon,
                    route_name=route,
                    permission_key=perm_key,
                    order=order,
                    is_active=True
                )
                session.add(menu)
                await session.flush()
            menu_objs[label] = menu

        await session.commit()
        print("Menus seeded.")

if __name__ == "__main__":
    asyncio.run(seed_data())
