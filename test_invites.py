
import requests
import uuid
import re

API_URL = "http://localhost:8000/api/v1"

def run_invite_test():
    session = requests.Session()
    
    # 1. Admin Signup
    admin_email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
    pwd = "password123"
    print(f"1. Signing up Admin {admin_email}...")
    
    resp = requests.post(f"{API_URL}/signup", json={"email": admin_email, "password": pwd})
    if resp.status_code != 200:
        print(f"Signup failed: {resp.text}")
        exit(1)
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Extract Org ID (implicit check)
    # We can check by creating a form
    resp = requests.post(f"{API_URL}/forms/", json={"title": "Shared Form", "slug": f"share-{uuid.uuid4().hex[:6]}"}, headers=admin_headers)
    form_id = resp.json()["id"]
    print(f"   Success. Created form {form_id}.")

    # 3. Send Invite
    memeber_email = f"member_{uuid.uuid4().hex[:6]}@example.com"
    print(f"2. Inviting {memeber_email}...")
    resp = requests.post(f"{API_URL}/invite", params={"email": memeber_email}, headers=admin_headers)
    if resp.status_code != 200:
        print(f"Invite failed: {resp.text}")
        exit(1)
    
    # In a real test, we'd read email logs. Here, the API returns the token for convenience/mocking if we coded it that way?
    # Wait, looking at login.py: return {"message": "Invite sent", "token": invite.token}
    token = resp.json().get("token")
    if not token:
        print("FAIL: No token returned in mock response.")
        exit(1)
    print(f"   Success. Token: {token}")

    # 4. Join
    print("3. Joining Organization...")
    resp = requests.post(f"{API_URL}/join", json={"token": token, "password": "newpassword123"})
    if resp.status_code != 200:
        print(f"Join failed: {resp.text}")
        exit(1)
    
    member_token = resp.json()["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}
    print("   Success. Joined.")

    # 5. Verify Access (Member should see Admin's form)
    print("4. Verifying Shared Access...")
    resp = requests.get(f"{API_URL}/forms/", headers=member_headers)
    forms = resp.json()
    
    found = False
    for f in forms:
        if f["id"] == form_id:
            found = True
            break
            
    if found:
        print("   Success. Member can see Admin's form.")
    else:
        print(f"FAIL: Member could not see Admin's form. Forms visible: {len(forms)}")
        exit(1)

    print("INVITE TEST PASSED.")

if __name__ == "__main__":
    run_invite_test()
