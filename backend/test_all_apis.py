import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        print("\n--- 1. Creating Institute (test_institute) ---")
        res = await ac.post("/api/v1/institutes", json={
            "name": "Test Institute",
            "slug": "test_institute",
            "address": "Test Address",
            "admin_email": "admin@test.com",
            "admin_password": "password"
        })
        print(res.status_code, res.json())
        if res.status_code not in (200, 201) and res.json().get('detail') != 'Institute with this slug already exists':
            print("Failed to create institute.")
            return

        tenant_header = {"X-Tenant-Slug": "test_institute"}

        print("\n--- 2. Registering Super Admin ---")
        res = await ac.post("/api/v1/auth/register", headers=tenant_header, json={
            "email": "super@test.com",
            "password": "password",
            "full_name": "Test Super Admin",
            "user_type": "super_admin"
        })
        print(res.status_code, res.json())

        print("\n--- 3. Logging in ---")
        res = await ac.post("/api/v1/auth/login", data={
            "username": "super@test.com",
            "password": "password"
        }, headers={"Content-Type": "application/x-www-form-urlencoded", **tenant_header})
        print(res.status_code, res.json())
        token = res.json().get("access_token")
        if not token:
            print("Login failed!")
            return
            
        auth_headers = {"Authorization": f"Bearer {token}", **tenant_header}

        print("\n--- 4. Creating Branch ---")
        res = await ac.post("/api/v1/branches", headers=auth_headers, json={
            "name": "Branch 1"
        })
        print(res.status_code, res.json())
        branch_id = res.json().get("id")

        print("\n--- 5. Creating Academic Year ---")
        res = await ac.post("/api/v1/academic/years", headers=auth_headers, json={
            "name": "2026-2027",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        })
        print(res.status_code, res.json())
        year_id = res.json().get("id")

        print("\n--- 6. Creating Class ---")
        res = await ac.post("/api/v1/academic/classes", headers=auth_headers, json={
            "name": "Class 10",
            "level": "Secondary"
        })
        print(res.status_code, res.json())
        class_id = res.json().get("id")

        print("\n--- 7. Creating Section ---")
        res = await ac.post("/api/v1/academic/sections", headers=auth_headers, json={
            "name": "Section A",
            "class_id": class_id,
            "branch_id": branch_id
        })
        print(res.status_code, res.json())
        section_id = res.json().get("id")

        print("\n--- 8. Creating Subject ---")
        res = await ac.post("/api/v1/academic/subjects", headers=auth_headers, json={
            "name": "Math",
            "code": "M101",
            "class_id": class_id
        })
        print(res.status_code, res.json())
        subject_id = res.json().get("id")

        print("\n--- 9. Creating Guardian ---")
        res = await ac.post("/api/v1/student/guardians", headers=auth_headers, json={
            "name": "John Guardian",
            "phone": "01700000000",
            "email": "guardian@test.com"
        })
        print(res.status_code, res.json())
        guardian_id = res.json().get("id")

        print("\n--- 10. Creating Student ---")
        res = await ac.post("/api/v1/student/students", headers=auth_headers, json={
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": "2010-01-01",
            "gender": "male",
            "guardian_id": guardian_id,
            "branch_id": branch_id
        })
        print(res.status_code, res.json())
        student_id = res.json().get("id")

        print("\n--- 11. Creating Enrollment ---")
        res = await ac.post("/api/v1/student/enrollments", headers=auth_headers, json={
            "enrollment_number": "ENR-001",
            "enrollment_date": "2026-01-01",
            "student_id": student_id,
            "academic_year_id": year_id,
            "class_id": class_id,
            "section_id": section_id
        })
        print(res.status_code, res.json())
        enrollment_id = res.json().get("id")

        print("\n--- 12. Creating Exam ---")
        res = await ac.post("/api/v1/exam/", headers=auth_headers, json={
            "name": "Half Yearly",
            "start_date": "2026-06-01",
            "end_date": "2026-06-15",
            "academic_year_id": year_id
        })
        print(res.status_code, res.json())
        exam_id = res.json().get("id")

        print("\n--- 13. Creating Exam Schedule ---")
        res = await ac.post("/api/v1/exam/schedules", headers=auth_headers, json={
            "exam_id": exam_id,
            "subject_id": subject_id,
            "exam_date": "2026-06-05",
            "start_time": "10:00:00",
            "end_time": "13:00:00"
        })
        print(res.status_code, res.json())
        schedule_id = res.json().get("id")

        print("\n--- 14. Creating Exam Result ---")
        res = await ac.post("/api/v1/exam/results", headers=auth_headers, json={
            "enrollment_id": enrollment_id,
            "exam_schedule_id": schedule_id,
            "obtained_marks": 85.5,
            "grade": "A+"
        })
        print(res.status_code, res.json())

        print("\n--- ALL TESTS COMPLETED ---")

if __name__ == "__main__":
    asyncio.run(main())
