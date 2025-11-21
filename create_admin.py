import requests

BASE_URL = 'http://127.0.0.1:5001/api'

def create_admin():
    username = "admin"
    password = "adminpassword123"
    email = "admin@example.com"
    
    print(f"Registering {username}...")
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username, 
        "email": email, 
        "password": password, 
        "role": "admin"
    })
    print(res.status_code, res.json())

if __name__ == "__main__":
    create_admin()
