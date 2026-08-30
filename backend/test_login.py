import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        print("--- Testing Login ---")
        response = await ac.post(
            "/api/v1/auth/login",
            data={
                "username": "admin@ems.com",
                "password": "password123"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Tenant-Slug": "global"
            }
        )
        print("Login Status Code:", response.status_code)
        print("Login Response:", response.json())
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("\n--- Testing Authenticated Endpoint (GET /academic/classes) ---")
            res2 = await ac.get(
                "/api/v1/academic/classes", 
                headers={
                    "Authorization": f"Bearer {token}", 
                    "X-Tenant-Slug": "global"
                }
            )
            print("Classes Status:", res2.status_code)
            print("Classes Response:", res2.json())

if __name__ == "__main__":
    asyncio.run(test_login())
