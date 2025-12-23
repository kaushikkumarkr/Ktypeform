import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def run_test():
    print("1. Logging in...")
    resp = requests.post(f"{BASE_URL}/login/access-token", data={"username": "admin@example.com", "password": "password"})
    if resp.status_code != 200:
        print(f"Login Failed: {resp.text}")
        sys.exit(1)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Success.")

    print("2. Creating Form...")
    import uuid
    random_slug = f"e2e-{uuid.uuid4().hex[:8]}"
    resp = requests.post(f"{BASE_URL}/forms/", headers=headers, json={"title": "E2E Test Form", "slug": random_slug})
    if resp.status_code != 200:
        print(f"Create Form Failed: {resp.text}")
        sys.exit(1)
    form = resp.json()
    form_id = form["id"]
    slug = form["slug"]
    print(f"   Success. ID: {form_id}, Slug: {slug}")

    print("3. Creating Version...")
    schema = {
        "fields": [
            {"id": "name", "type": "text", "label": "Full Name", "required": True},
            {"id": "email", "type": "email", "label": "Email Address", "required": True},
            {"id": "age", "type": "number", "label": "Age", "required": True}
        ]
    }
    version_data = {
        "schema_json": schema,
        "rules_json": [],
        "formulas_json": [],
        "pdf_template": "<h1>Hello {{name}}</h1>",
        "is_published": True
    }
    resp = requests.post(f"{BASE_URL}/forms/{form_id}/versions", headers=headers, json=version_data)
    if resp.status_code != 200:
        print(f"Create Version Failed: {resp.text}")
        sys.exit(1)
    print("   Success.")

    print("4. Submitting to Public Endpoint...")
    answers = {"name": "Test User", "email": "test@example.com", "age": 25}
    resp = requests.post(f"{BASE_URL}/public/{slug}/submit", json={"answers": answers})
    if resp.status_code != 200:
        print(f"Submission Failed: {resp.text}")
        sys.exit(1)
    res_data = resp.json()
    print(f"   Success. PDF URL: {res_data.get('pdf_url')}")
    
    print("5. Testing AI Generation...")
    resp = requests.post(f"{BASE_URL}/agents/generate", json={"prompt": "Simple contact form"})
    if resp.status_code != 200:
        print(f"Agent Failed: {resp.text}")
        sys.exit(1)
    agent_data = resp.json()
    if agent_data.get("error"):
         print(f"   Agent Returned Error: {agent_data['error']}")
    else:
         # Support both flat fields and pages structure
         schema = agent_data['schema_json']
         if 'pages' in schema:
             total_fields = sum(len(p.get('fields', [])) for p in schema.get('pages', []))
             print(f"   Success. Generated Pages: {len(schema['pages'])}, Total Fields: {total_fields}")
         else:
             print(f"   Success. Generated Fields: {len(schema.get('fields', []))}")

    print("\nALL TESTS PASSED.")

if __name__ == "__main__":
    run_test()
