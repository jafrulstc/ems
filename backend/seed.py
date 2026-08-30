import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.core.config import settings
from app.models.auth import User
from app.models.tenant import Institute, Branch
from app.models.academic import AcademicYear, AcademicClass, Section, Subject
from app.core.security import get_password_hash
from datetime import date

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Institute).where(Institute.slug == "global"))
        if result.scalar_one_or_none():
            print("Database already seeded!")
            return

        # 1. Create Institute
        institute = Institute(name="Global School", slug="global", address="Dhaka")
        session.add(institute)
        await session.flush()
        
        # 2. Create Super Admin
        super_admin = User(
            email="admin@ems.com",
            hashed_password=get_password_hash("password123"),
            full_name="Super Admin",
            user_type="super_admin",
            tenant_id=institute.id
        )
        session.add(super_admin)
        
        # 3. Create a Branch
        branch = Branch(name="Main Branch", address="Dhaka", tenant_id=institute.id)
        session.add(branch)
        await session.flush()
        
        # 4. Create Academic Year
        ay = AcademicYear(name="2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), tenant_id=institute.id)
        session.add(ay)
        await session.flush()
        
        # 5. Create Class
        cls = AcademicClass(name="Class 10", level="Secondary", tenant_id=institute.id)
        session.add(cls)
        await session.flush()
        
        # 6. Create Section
        sec = Section(name="A", class_id=cls.id, branch_id=branch.id, tenant_id=institute.id)
        session.add(sec)
        
        await session.commit()
        print("Seed data inserted successfully!")
        print("---------------------------------")
        print("Super Admin Login: admin@ems.com")
        print("Password: password123")
        print("Tenant Slug (Header X-Tenant-Slug): global")
        print("---------------------------------")

if __name__ == "__main__":
    asyncio.run(seed())
