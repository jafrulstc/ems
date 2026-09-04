import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.session import engine
from app.models.academic import AcademicClass, AcademicYear, Subject, YearlyClassSubject
from app.models.tenant import Institute

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def patch():
    async with AsyncSessionLocal() as session:
        stmt = select(Institute).where(Institute.slug.like("%test%"))
        result = await session.execute(stmt)
        institute = result.scalars().first()
        if not institute:
            stmt = select(Institute).where(Institute.slug == "tahzibul-ummah")
            result = await session.execute(stmt)
            institute = result.scalars().first()
            
        if not institute:
            return
            
        tenant_id = institute.id
        
        # Get AY
        ay = (await session.execute(select(AcademicYear).where(AcademicYear.tenant_id == tenant_id))).scalars().first()
        # Get Class
        cls = (await session.execute(select(AcademicClass).where(AcademicClass.tenant_id == tenant_id))).scalars().first()
        # Get Subjects
        subjects = (await session.execute(select(Subject).where(Subject.tenant_id == tenant_id))).scalars().all()
        
        if ay and cls and subjects:
            for subj in subjects:
                # Check if exists
                existing = (await session.execute(
                    select(YearlyClassSubject).where(
                        YearlyClassSubject.academic_year_id == ay.id,
                        YearlyClassSubject.class_id == cls.id,
                        YearlyClassSubject.subject_id == subj.id
                    )
                )).scalars().first()
                if not existing:
                    ycs = YearlyClassSubject(
                        academic_year_id=ay.id,
                        class_id=cls.id,
                        subject_id=subj.id,
                        tenant_id=tenant_id
                    )
                    session.add(ycs)
            await session.commit()
            print("Patch completed successfully.")

if __name__ == "__main__":
    asyncio.run(patch())
