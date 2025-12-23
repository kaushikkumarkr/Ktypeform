
import requests
import uuid

API_URL = "http://localhost:8000/api/v1"

def run_api_key_test():
    # 1. Login as Admin
    print("1. Logging in as admin...")
    resp = requests.post(f"{API_URL}/login/access-token", data={"username": "admin@example.com", "password": "password"})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        exit(1)
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   Success.")

    # 2. Create API Key
    print("2. Creating API Key...")
    resp = requests.post(f"{API_URL}/api-keys", json={"name": "Test Key"}, headers=headers)
    if resp.status_code != 200:
        print(f"Create key failed: {resp.text}")
        exit(1)
    key_data = resp.json()
    raw_key = key_data["key"]
    key_id = key_data["id"]
    print(f"   Success. Key: {raw_key[:20]}...")

    # 3. Use API Key to access /forms
    print("3. Accessing /forms with API Key...")
    resp = requests.get(f"{API_URL}/forms/", headers={"X-API-Key": raw_key})
    if resp.status_code != 200:
        print(f"API Key access failed: {resp.text}")
        exit(1)
    forms = resp.json()
    print(f"   Success. Forms visible: {len(forms)}")

    # 4. List API Keys
    print("4. Listing API Keys...")
    resp = requests.get(f"{API_URL}/api-keys", headers=headers)
    if resp.status_code != 200:
        print(f"List keys failed: {resp.text}")
        exit(1)
    keys = resp.json()
    print(f"   Success. Keys: {len(keys)}")

    # 5. Revoke API Key
    print("5. Revoking API Key...")
    resp = requests.delete(f"{API_URL}/api-keys/{key_id}", headers=headers)
    if resp.status_code != 200:
        print(f"Revoke failed: {resp.text}")
        exit(1)
    print("   Success. Key revoked.")

    # 6. Verify Revoked Key Fails
    print("6. Verifying revoked key is denied...")
    resp = requests.get(f"{API_URL}/forms/", headers={"X-API-Key": raw_key})
    if resp.status_code == 401:
        print("   Success. Revoked key denied.")
    else:
        print(f"FAIL: Revoked key still works! Status: {resp.status_code}")
        exit(1)

    print("API KEY TEST PASSED.")

if __name__ == "__main__":
    run_api_key_test()
