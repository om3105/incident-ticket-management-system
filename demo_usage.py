import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5001/api'

def run_demo():
    username = f"demo_user_{int(time.time())}"
    email = f"{username}@example.com"
    password = "password123"
    
    print(f"Registering {username}...")
    res = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "email": email, "password": password, "role": "user"})
    print(res.status_code, res.json())
    
    if res.status_code != 201: return

    print("Logging in...")
    res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    print(res.status_code, res.json())
    
    if res.status_code != 200: return
    token = res.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    print("Creating ticket...")
    res = requests.post(f"{BASE_URL}/tickets", json={"title": "Demo Ticket", "description": "Test desc", "priority": "high"}, headers=headers)
    print(res.status_code, res.json())

    print("Fetching tickets...")
    res = requests.get(f"{BASE_URL}/tickets", headers=headers)
    print(res.status_code, res.json())

if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"Error: {e}")
