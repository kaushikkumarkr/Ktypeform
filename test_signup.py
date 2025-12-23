
import requests
import uuid
import time

API_URL = "http://localhost:8000/api/v1"

def run_signup_test():
    session = requests.Session()
    
    unique_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    password = "password123"
    
    # 1. Signup
    print(f"1. Signing up as {unique_email}...")
    resp = requests.post(f"{API_URL}/signup", json={"email": unique_email, "password": password})
    if resp.status_code != 200:
        print(f"Signup failed: {resp.text}")
        exit(1)
    
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Success. Token received.")

    # 2. Verify Forms (Should be empty initially)
    print("2. Verifying Dashboard Isolation...")
    resp = session.get(f"{API_URL}/forms/", headers=headers)
    if resp.status_code != 200:
        print(f"Get forms failed: {resp.text}")
        exit(1)
        
    forms = resp.json()
    if len(forms) != 0:
        print(f"FAIL: Expected 0 forms for new user, got {len(forms)}")
        # This confirms that this new user does NOT see the 'admin' forms created in previous tests
        exit(1)
    print("   Success. New workspace is empty.")

    # 3. Create a Form
    print("3. Creating Form in new workspace...")
    resp = session.post(f"{API_URL}/forms/", json={"title": "My Private Form", "slug": f"private-{uuid.uuid4().hex[:6]}"}, headers=headers)
    if resp.status_code != 200:
        print(f"Create form failed: {resp.text}")
        exit(1)
    print("   Success. Form created.")
    
    print("SIGNUP TEST PASSED.")

if __name__ == "__main__":
    run_signup_test()
