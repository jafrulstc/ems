import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.models.auth import User
from app.models.tenant import Institute, Branch
from app.models.academic import AcademicYear, AcademicClass, Section, Subject
from app.core.security import get_password_hash
from datetime import date

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def drop_all_data():
    """Drop all data from all schemas (order matters for FK constraints)"""
    async with engine.begin() as conn:
        schemas = ["exam", "student", "academic", "auth", "tenant"]
        for schema in schemas:
            result = await conn.execute(text(
                f"SELECT tablename FROM pg_tables WHERE schemaname = '{schema}' ORDER BY tablename"
            ))
            tables = result.fetchall()
            if tables:
                table_names = ", ".join([f"{schema}.{t[0]}" for t in tables])
                await conn.execute(text(f"TRUNCATE TABLE {table_names} CASCADE"))
        print("[OK] All data dropped.")

async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Institute).where(Institute.slug == "test_institute")
        )
        if result.scalar_one_or_none():
            print("Already seeded. Skipping.")
            return

        # 1. Institute
        institute = Institute(
            name="TEST_INSTITUTE",
            slug="test_institute",
            address="Dhaka, Bangladesh",
            contact_email="admin@test-institute.edu.bd"
        )
        session.add(institute)
        await session.flush()

        # 2. Branch  (create BEFORE user — user needs branch_id)
        branch = Branch(name="Main Branch", address="Dhaka", tenant_id=institute.id)
        session.add(branch)
        await session.flush()

        # 3. Admin User  — assigned to Main Branch
        admin = User(
            email="admin@test-institute.edu.bd",
            hashed_password=get_password_hash("Admin@1234"),
            full_name="System Administrator",
            user_type="admin",
            tenant_id=institute.id,
            branch_id=branch.id,
        )
        session.add(admin)

        # 4. Academic Year  (institute-wide, no branch)
        ay = AcademicYear(
            name="2026",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            tenant_id=institute.id,
        )
        session.add(ay)
        await session.flush()

        # 5. Class  (institute-wide, shared across branches)
        cls = AcademicClass(name="Class 10", level="Secondary", tenant_id=institute.id)
        session.add(cls)
        await session.flush()

        # 6. Section  (branch-specific)
        sec = Section(name="A", class_id=cls.id, branch_id=branch.id, tenant_id=institute.id)
        session.add(sec)

        await session.commit()
        print("[OK] Seed complete.")
        print("-" * 45)
        print("  Institute  : TEST_INSTITUTE")
        print("  Branch     : Main Branch")
        print("  Admin Email: admin@test-institute.edu.bd")
        print("  Password   : Admin@1234")
        print("-" * 45)

async def main():
    import sys
    if "--drop" in sys.argv:
        await drop_all_data()
    await seed()

if __name__ == "__main__":
    asyncio.run(main())
