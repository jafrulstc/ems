import asyncio

import asyncpg

from app.core.config import settings


async def main():
    conn = await asyncpg.connect(settings.DATABASE_URL.replace("+asyncpg", ""))
    await conn.execute('CREATE SCHEMA IF NOT EXISTS tenant;')
    await conn.execute('CREATE SCHEMA IF NOT EXISTS auth;')
    await conn.execute('CREATE SCHEMA IF NOT EXISTS academic;')
    await conn.execute('CREATE SCHEMA IF NOT EXISTS student;')
    await conn.execute('CREATE SCHEMA IF NOT EXISTS exam;')
    await conn.close()
    print("Schemas created successfully")

if __name__ == "__main__":
    asyncio.run(main())
