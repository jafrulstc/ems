from enum import StrEnum

class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    INSTITUTE_ADMIN = "institute_admin"
    BRANCH_ADMIN = "branch_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    GUARDIAN = "guardian"
