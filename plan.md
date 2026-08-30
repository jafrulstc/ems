# Project Plan: Education Management System (EMS)

## 1. Project Overview
এটি একটি মাল্টি-টেন্যান্ট Education Management System (EMS), যেখানে একাধিক ইনস্টিটিউট এবং তাদের শাখাগুলো ম্যানেজ করা যাবে। সিস্টেমটিতে ফাইন-গ্রেইনড RBAC (Role-Based Access Control), Data Scoping বা ABAC ভিত্তিক RLAC (Row-Level Access Control), এবং Soft Delete ফিচার থাকবে।

## 2. Tech Stack
**Backend**
* Language: Python (>=3.12 বা 3.13)
* Framework: FastAPI
* Database: PostgreSQL
* ORM: SQLAlchemy 2.0 (Async)
* Migrations: Alembic
* Validation: Pydantic v2
* Auth: python-jose (JWT), argon2-cffi (Password Hashing)
* Other Packages: asyncpg, boto3, cloudinary, httpx, playwright

**Frontend**
* Framework: Vue 3 (Composition API)
* State Management: Pinia
* Routing: Vue Router
* UI Library: PrimeVue,(Primeuix themes)
* Data Fetching: @tanstack/vue-query
* Form Validation: Zod
* PDF & Excel: pdfmake, html2pdf.js, xlsx
* Build Tool: Vite

## 3. Core Architecture & Rules (Strictly Follow These)
**A. Multi-Tenancy (Shared Database, Shared Schema)**
* সব টেবিলে `tenant_id` (Institute ID) থাকবে।
* URL এর মাধ্যমে টেন্যান্ট আইডেন্টিফাই করা হবে (Path-based: ems.com/abcinstitute)।
* ফ্রন্টএন্ড থেকে ব্যাকএন্ডে রিকোয়েস্ট পাঠানোর সময় `X-Tenant-Slug` (যেমন: abcinstitute) নামে একটি হেডার পাঠানো হবে।
* ব্যাকএন্ড এটি ভেরিফাই করে JWT টোকেনের সাথে মিলিয়ে `tenant_id` বের করবে।

**B. RBAC, Data Scoping (RLAC) & Granular Permissions**
* শুধু Role (Admin/Teacher) নয়, প্রতিটি অ্যাকশনের জন্য আলাদা পারমিশন থাকবে (যেমন: `student:read`, `student:create`)।
* JWT টোকেনের ভেতর ইউজারের পারমিশন লিস্ট এবং Data Scope (যেমন: branch_ids, class_ids) থাকবে।
* FastAPI Dependency (`require_permission("student:read")`) তৈরি করে প্রতিটি রাউট প্রটেক্ট করতে হবে।
* **Data-Level Security:** SQLAlchemy এর `with_loader_criteria` ব্যবহার করে Data Scoping অ্যাপ্লাই করার সময় অবশ্যই `hasattr()` দিয়ে চেক করতে হবে মডেলে ওই কলামটি (যেমন: `branch_id`, `class_id`) আছে কিনা। অন্যথায় গ্লোবাল ফিল্টারে এরর আসবে।
* ফ্রন্টএন্ডে পারমিশন লিস্টের ওপর ভিত্তি করে UI হাইড/শো করার জন্য `v-permission` ডিরেকটিভ তৈরি করতে হবে।

**C. Soft Delete**
* কোনো ডাটা সরাসরি (Hard Delete) ডিলিট করা যাবে না।
* প্রতিটি টেবিলে `is_deleted` (Boolean, default=False) থাকবে।
* ডিলিট করার সময় শুধু `is_deleted = True` সেট করতে হবে।

**D. Database Enum Strategy**
* PostgreSQL-এ কোনো ENUM টাইপ ব্যবহার করা যাবে না।
* সব ডাটাবেস ফিল্ড String টাইপের হবে।
* Python-এ `enum.StrEnum` ক্লাস তৈরি করে Pydantic-এর মাধ্যমে ভ্যালিডেশন করতে হবে।

**E. Base Model & Mixins**
* Base (DeclarativeBase)
* UUIDMixin: Primary Key হিসেবে UUID (default=uuid.uuid4)
* TimestampMixin: created_at, updated_at
* TenantMixin: tenant_id
* SoftDeleteMixin: is_deleted

## 4. Step-by-Step Implementation Plan (Phases)

**Phase 1: Core Architecture & Database Setup**
* Task 1.1: FastAPI প্রজেক্ট স্ট্রাকচার তৈরি (api, core, db, models, schemas, services, repositories)।
* Task 1.2: core/config.py এ Pydantic Settings এবং db/session.py এ Async Engine/Session সেটআপ।
* Task 1.3: db/base.py এ Base মডেল ও Mixins (UUID, Timestamp, Tenant, SoftDelete) তৈরি।
* Task 1.4: core/enums.py এ Python StrEnum তৈরি।
* Task 1.5: Alembic কনফিগার করা এবং Async মাইগ্রেশন জেনারেট করা।

**Phase 2: Authentication & Multi-Tenancy Implementation**
* Task 2.1: Institute (Tenant), Branch, User, Role, Permission মডেল তৈরি।
* Task 2.2: Tenant Middleware বা Dependency (get_tenant_from_slug) তৈরি (X-Tenant-Slug হেডার থেকে)।
* Task 2.3: Auth APIs (/auth/login, /auth/register)। Argon2 ও JWT ইমপ্লিমেন্টেশন।
* Task 2.4: get_current_user ডিপেন্ডেন্সি তৈরি।

**Phase 3: RBAC & Data-Level Security (RLAC) [UPDATED]**
* Task 3.1: require_permission(perm_name) ডিপেন্ডেন্সি তৈরি (যেমন: student:read)।
* Task 3.2: DataScope বা UserContext মডেল তৈরি। লগইন করার সময় ইউজারের রোল অনুযায়ী তার ডাটা দেখার সীমা (branch_ids, class_ids, student_ids) ডাটাবেস থেকে এক্সট্র্যাক্ট করে JWT টোকেনে বা সেশনে রাখা।
* Task 3.3: SQLAlchemy এর `with_loader_criteria` ব্যবহার করে অটোমেটিক ফিল্টারিং (Automated RLAC) ইমপ্লিমেন্ট করা:
  * অটোমেটিক `tenant_id` ফিল্টার (মাল্টিটেন্যান্সি)।
  * অটোমেটিক `is_deleted = False` ফিল্টার (সফট ডিলিট)।
  * **অটোমেটিক Data Scoping (Safety Check সহ):**
    * Branch Admin হলে: `if hasattr(entity, "branch_id"): entity.branch_id == user.branch_id`
    * Teacher হলে: `if hasattr(entity, "class_id"): entity.class_id.in_(user.class_ids)`
    * Guardian হলে: `if hasattr(entity, "id"): entity.id.in_(user.student_ids)`
* Task 3.4: Frontend Axios ইন্টারসেপ্টর সেটআপ (URL থেকে slug পার্স করে হেডারে পাঠানো)।

**Phase 4: Core & Academic Module**
* Task 4.1: Institute ও Branch এর CRUD APIs (Super Admin)।
* Task 4.2: AcademicYear, Semester, Class, Section, Subject মডেল ও CRUD APIs।
* Task 4.3: Frontend Vue রাউটার, Pinia Auth Store, PrimeVue UI সেটআপ।
* Task 4.4: Frontend-এ v-permission ডিরেকটিভ তৈরি ও Navigation Guard সেটআপ।

**Phase 5: Students & Enrollments Module**
* Task 5.1: Student, Guardian মডেল ও CRUD APIs।
* Task 5.2: Cloudinary/Boto3 ইন্টিগ্রেশন (ছবি/ডকুমেন্ট আপলোড)।
* Task 5.3: Enrollment মডেল ও এনরোলমেন্ট API।
* Task 5.4: Frontend-এ PrimeVue DataTable দিয়ে স্টুডেন্ট ম্যানেজমেন্ট UI এবং xlsx দিয়ে বাল্ক এনরোলমেন্ট।

**Phase 6: Exams Module**
* Task 6.1: Exam, ExamSchedule, Marks মডেল ও APIs।
* Task 6.2: রেজাল্ট ক্যালকুলেশন ও পাবলিশ করার লজিক।
* Task 6.3: Frontend-এ রুটিন ক্যালেন্ডার, মার্কস এন্ট্রি ফর্ম এবং pdfmake দিয়ে PDF রেজাল্ট শিট জেনারেশন।

**Phase 7: Testing & Deployment**
* Task 7.1: Playwright দিয়ে E2E টেস্ট।
* 


## 5. Initial Reference Code (For Context)

**backend/app/core/config.py**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Education Management System"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ems_db"
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

backend/app/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


backend/app/db/base.py

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime, func
from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TenantMixin:
    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)


backend/app/core/enums.py

from enum import StrEnum

class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    INSTITUTE_ADMIN = "institute_admin"
    BRANCH_ADMIN = "branch_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    GUARDIAN = "guardian"