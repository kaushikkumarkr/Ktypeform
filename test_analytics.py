
import requests
import uuid
import time

API_URL = "http://localhost:8000/api/v1"
EMAIL = "admin@example.com"
PASSWORD = "password"

def run_analytics_test():
    session = requests.Session()
    
    # 1. Login
    print("1. Logging in...")
    resp = session.post(f"{API_URL}/login/access-token", data={"username": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        exit(1)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Success.")

    # 2. Create Form
    print("2. Creating Form...")
    slug = f"analytics-{uuid.uuid4().hex[:8]}"
    form_data = {"title": "Analytics Test Form", "slug": slug}
    resp = session.post(f"{API_URL}/forms/", json=form_data, headers=headers)
    if resp.status_code != 200:
        print(f"Create form failed: {resp.text}")
        exit(1)
    form_id = resp.json()["id"]
    print(f"   Success. ID: {form_id}, Slug: {slug}")

    # 3. Publish Version
    print("3. Creating Version...")
    version_data = {
        "schema_json": {
            "title": "Analytics Form",
            "fields": [
                {"id": "name", "type": "text", "label": "Name", "required": True},
                {"id": "rating", "type": "number", "label": "Rating", "required": True}
            ]
        },
        "rules_json": [],
        "formulas_json": [],
        "pdf_template": "<h1>Rating: {{rating}}</h1>",
        "is_published": True
    }
    resp = session.post(f"{API_URL}/forms/{form_id}/versions", json=version_data, headers=headers)
    if resp.status_code != 200:
        print(f"Create version failed: {resp.text}")
        exit(1)
    print("   Success.")

    # 4. Submit Multiple Times
    print("4. Submitting 5 entries...")
    for i in range(5):
        data = {"answers": {"name": f"User {i}", "rating": i*2}}
        resp = requests.post(f"{API_URL}/public/{slug}/submit", json=data)
        if resp.status_code != 200:
            print(f"Submission {i} failed: {resp.text}")
        print(f"   Submitted {i+1}")
        time.sleep(0.1) 

    # 5. Check Stats
    print("5. Checking Stats...")
    resp = session.get(f"{API_URL}/forms/{form_id}/stats", headers=headers)
    if resp.status_code != 200:
        print(f"Get stats failed: {resp.text}")
        exit(1)
    
    stats = resp.json()
    print("   Stats Response:")
    print(stats)
    
    # Assertions
    if stats["total_submissions"] != 5:
        print(f"FAIL: Expected 5 submissions, got {stats['total_submissions']}")
        exit(1)
    
    if len(stats["recent_submissions"]) != 5:
        print(f"FAIL: Expected 5 recent submissions, got {len(stats['recent_submissions'])}")
        exit(1)
        
    print("ANALYTICS TEST PASSED.")

if __name__ == "__main__":
    run_analytics_test()
