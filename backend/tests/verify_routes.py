"""
Integration Test to verify all core Flask routes work properly end-to-end.
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app

def run_verification():
    print("\n" + "="*55)
    print("Running End-to-End API Route Verification...")
    print("="*55)

    client = app.test_client()

    # 1. Root route
    res = client.get('/')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 1. GET /                          -> Status 200 ({res.get_json()['status']})")

    # 2. Login (Admin)
    res = client.post('/api/login', json={'username': 'admin', 'password': 'password123'})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_data(as_text=True)}"
    data = res.get_json()
    print(f"[OK] 2. POST /api/login                -> Status 200 (Logged in as: {data.get('username')})")

    # 3. Current User
    res = client.get('/api/current-user')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 3. GET /api/current-user          -> Status 200 (Role: {res.get_json().get('role')})")

    # 4. Courses
    res = client.get('/api/courses')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    courses = res.get_json()
    print(f"[OK] 4. GET /api/courses               -> Status 200 (Loaded {len(courses)} courses)")

    # 5. Course Details
    if courses:
        course_id = courses[0]['id']
        res = client.get(f'/api/courses/{course_id}')
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        print(f"[OK] 5. GET /api/courses/{course_id}           -> Status 200 (Course: {res.get_json().get('name')})")

    # 6. Agent Status
    res = client.get('/api/agent-status')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 6. GET /api/agent-status          -> Status 200 (Agent status: {res.get_json().get('status')})")

    # 7. Agent Analytics
    res = client.get('/api/agent-analytics')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 7. GET /api/agent-analytics       -> Status 200 (Analytics active)")

    # 8. Progress Summary
    res = client.get('/api/progress-summary')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 8. GET /api/progress-summary      -> Status 200 (Subtopics: {res.get_json().get('total_subtopics')})")

    # 9. Recommendation
    res = client.get('/api/recommendations/next-topic')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 9. GET /api/recommendations/...   -> Status 200 ({res.get_json().get('recommendation')})")

    # 10. Code Execution Sandbox
    res = client.post('/api/check-code', json={'code': 'print("Hello from AI Tutor!")'})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 10. POST /api/check-code          -> Status 200 ({res.get_json().get('output').strip()})")

    # 11. Logout
    res = client.post('/api/logout')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print(f"[OK] 11. POST /api/logout              -> Status 200 (Session cleared)")

    print("="*55)
    print("ALL 11 END-TO-END VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("="*55 + "\n")

if __name__ == '__main__':
    run_verification()
