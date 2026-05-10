"""
Migration: 0003 — Seed superuser, default organization, and all permission keys.

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1

Superuser credentials (change APP_SUPERUSER_PASSWORD env var in production):
  org_slug : default
  email    : admin@ems.local
  password : Admin@123456  (override via APP_SUPERUSER_PASSWORD env var)
"""
import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a1b2"
down_revision: Union[str, None] = "b2c3d4e5f6a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# All system permission keys
_PERMISSIONS = [
    # Core
    ("core.academic_years.view",   "View Academic Years",   "core",     "view"),
    ("core.academic_years.create", "Create Academic Years", "core",     "create"),
    ("core.academic_years.edit",   "Edit Academic Years",   "core",     "edit"),
    ("core.academic_years.delete", "Delete Academic Years", "core",     "delete"),
    ("core.menus.view",            "View Menus",            "core",     "view"),
    ("core.menus.create",          "Create Menus",          "core",     "create"),
    ("core.menus.edit",            "Edit Menus",            "core",     "edit"),
    ("core.menus.delete",          "Delete Menus",          "core",     "delete"),
    ("core.settings.view",         "View Settings",         "core",     "view"),
    ("core.settings.create",       "Create Settings",       "core",     "create"),
    ("core.settings.edit",         "Edit Settings",         "core",     "edit"),
    # Auth
    ("auth.users.view",            "View Users",            "auth",     "view"),
    ("auth.users.create",          "Create Users",          "auth",     "create"),
    ("auth.users.edit",            "Edit Users",            "auth",     "edit"),
    ("auth.users.delete",          "Delete Users",          "auth",     "delete"),
    ("auth.roles.view",            "View Roles",            "auth",     "view"),
    ("auth.roles.create",          "Create Roles",          "auth",     "create"),
    ("auth.roles.edit",            "Edit Roles",            "auth",     "edit"),
    ("auth.roles.delete",          "Delete Roles",          "auth",     "delete"),
    ("auth.permissions.view",      "View Permissions",      "auth",     "view"),
    # Academic
    ("academic.classes.view",      "View Classes",          "academic", "view"),
    ("academic.classes.create",    "Create Classes",        "academic", "create"),
    ("academic.classes.edit",      "Edit Classes",          "academic", "edit"),
    ("academic.classes.delete",    "Delete Classes",        "academic", "delete"),
    ("academic.sections.view",     "View Sections",         "academic", "view"),
    ("academic.sections.create",   "Create Sections",       "academic", "create"),
    ("academic.sections.edit",     "Edit Sections",         "academic", "edit"),
    ("academic.sections.delete",   "Delete Sections",       "academic", "delete"),
    ("academic.subjects.view",     "View Subjects",         "academic", "view"),
    ("academic.subjects.create",   "Create Subjects",       "academic", "create"),
    ("academic.subjects.edit",     "Edit Subjects",         "academic", "edit"),
    ("academic.subjects.delete",   "Delete Subjects",       "academic", "delete"),
    ("academic.students.view",     "View Students",         "academic", "view"),
    ("academic.students.create",   "Create Students",       "academic", "create"),
    ("academic.students.edit",     "Edit Students",         "academic", "edit"),
    ("academic.students.delete",   "Delete Students",       "academic", "delete"),
    ("academic.enrollments.view",  "View Enrollments",      "academic", "view"),
    ("academic.enrollments.create","Create Enrollments",    "academic", "create"),
    ("academic.enrollments.edit",  "Edit Enrollments",      "academic", "edit"),
    ("academic.enrollments.delete","Delete Enrollments",    "academic", "delete"),
    ("academic.class_subjects.view",  "View Class Subjects",   "academic", "view"),
    ("academic.class_subjects.create","Create Class Subjects", "academic", "create"),
    # Exam
    ("exam.exam_types.view",       "View Exam Types",       "exam",     "view"),
    ("exam.exam_types.create",     "Create Exam Types",     "exam",     "create"),
    ("exam.exam_types.edit",       "Edit Exam Types",       "exam",     "edit"),
    ("exam.exam_types.delete",     "Delete Exam Types",     "exam",     "delete"),
    ("exam.routines.view",         "View Routines",         "exam",     "view"),
    ("exam.routines.create",       "Create Routines",       "exam",     "create"),
    ("exam.routines.edit",         "Edit Routines",         "exam",     "edit"),
    ("exam.routines.delete",       "Delete Routines",       "exam",     "delete"),
    ("exam.marks.view",            "View Marks",            "exam",     "view"),
    ("exam.marks.create",          "Create Marks",          "exam",     "create"),
    ("exam.marks.edit",            "Edit Marks",            "exam",     "edit"),
    ("exam.grading.view",          "View Grading Systems",  "exam",     "view"),
    ("exam.grading.create",        "Create Grading Systems","exam",     "create"),
    ("exam.grading.edit",          "Edit Grading Systems",  "exam",     "edit"),
    ("exam.grading.delete",        "Delete Grading Systems","exam",     "delete"),
    ("exam.results.view",          "View Results",          "exam",     "view"),
    ("exam.results.create",        "Generate Results",      "exam",     "create"),
    ("exam.attendance.view",       "View Attendance",       "exam",     "view"),
    ("exam.attendance.create",     "Enter Attendance",      "exam",     "create"),
]


def upgrade() -> None:
    from argon2 import PasswordHasher
    ph = PasswordHasher()

    conn = op.get_bind()

    # 1. Default organization
    org = conn.execute(
        sa.text(
            "INSERT INTO core.organizations (name, slug, is_active) "
            "VALUES ('Default School', 'default', true) RETURNING id"
        )
    ).fetchone()
    org_id = org[0]

    # 2. All permissions
    for key, label, module, action in _PERMISSIONS:
        conn.execute(
            sa.text(
                "INSERT INTO auth.permissions (key, label, module, action) "
                "VALUES (:key, :label, :module, :action) ON CONFLICT (key) DO NOTHING"
            ),
            {"key": key, "label": label, "module": module, "action": action},
        )

    # 3. Admin role
    role = conn.execute(
        sa.text(
            "INSERT INTO auth.roles (organization_id, name, description) "
            "VALUES (:org_id, 'Admin', 'Full access role') RETURNING id"
        ),
        {"org_id": org_id},
    ).fetchone()
    role_id = role[0]

    # 4. Assign all permissions to Admin role
    for key, _, _, _ in _PERMISSIONS:
        conn.execute(
            sa.text(
                "INSERT INTO auth.role_permissions (role_id, permission_id) "
                "SELECT :role_id, id FROM auth.permissions WHERE key = :key"
            ),
            {"role_id": role_id, "key": key},
        )

    # 5. Superuser
    raw_password = os.environ.get("APP_SUPERUSER_PASSWORD", "Admin@123456")
    hashed = ph.hash(raw_password)
    user = conn.execute(
        sa.text(
            "INSERT INTO auth.users (organization_id, email, hashed_password, full_name, is_active, is_superuser) "
            "VALUES (:org_id, 'admin@ems.local', :pwd, 'System Administrator', true, true) RETURNING id"
        ),
        {"org_id": org_id, "pwd": hashed},
    ).fetchone()
    user_id = user[0]

    # 6. Assign Admin role to superuser
    conn.execute(
        sa.text("INSERT INTO auth.user_roles (user_id, role_id) VALUES (:uid, :rid)"),
        {"uid": user_id, "rid": role_id},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM auth.user_roles"))
    conn.execute(sa.text("DELETE FROM auth.users WHERE email = 'admin@ems.local'"))
    conn.execute(sa.text("DELETE FROM auth.role_permissions"))
    conn.execute(sa.text("DELETE FROM auth.roles WHERE name = 'Admin'"))
    conn.execute(sa.text("DELETE FROM auth.permissions"))
    conn.execute(sa.text("DELETE FROM core.organizations WHERE slug = 'default'"))
