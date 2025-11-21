import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:5001/api"

if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None

def api_request(method, endpoint, data=None, params=None):
    headers = {'Authorization': f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        if method == 'GET': return requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params)
        if method == 'POST': return requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
        if method == 'PUT': return requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=data)
    except: return None

def login_page():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = api_request('POST', '/auth/login', {'username': username, 'password': password})
        if res and res.status_code == 200:
            data = res.json()
            st.session_state.token = data['token']
            st.session_state.user = data['user']
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.header("Register")
    new_user = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["user", "agent", "admin"])
    if st.button("Register"):
        res = api_request('POST', '/auth/register', {'username': new_user, 'email': new_email, 'password': new_pass, 'role': role})
        if res and res.status_code == 201: st.success("Registered! Please login.")

def dashboard():
    st.header("Dashboard")
    status = st.selectbox("Filter Status", ["All", "open", "in_progress", "resolved", "closed"])
    priority = st.selectbox("Filter Priority", ["All", "low", "medium", "high", "critical"])
    
    params = {}
    if status != "All": params['status'] = status
    if priority != "All": params['priority'] = priority
    
    res = api_request('GET', '/tickets', params=params)
    if res and res.status_code == 200:
        tickets = res.json().get('tickets', [])
        if tickets:
            df = pd.DataFrame(tickets)
            st.dataframe(df[['id', 'title', 'status', 'priority', 'created_at']])
            
            tid = st.number_input("Ticket ID", min_value=1, step=1)
            if tid:
                t_res = api_request('GET', f'/tickets/{tid}')
                if t_res and t_res.status_code == 200:
                    t = t_res.json().get('ticket')
                    st.write(f"Title: {t['title']}")
                    st.write(f"Desc: {t['description']}")
                    st.write(f"Status: {t['status']}")
                    
                    if st.session_state.user['role'] in ['agent', 'admin']:
                        new_stat = st.selectbox("New Status", ["open", "in_progress", "resolved", "closed"])
                        if st.button("Update"):
                            api_request('PUT', f'/tickets/{tid}', {'status': new_stat})
                            st.rerun()

def create_ticket():
    st.header("New Ticket")
    title = st.text_input("Title")
    desc = st.text_area("Description")
    prio = st.selectbox("Priority", ["low", "medium", "high", "critical"])
    if st.button("Submit"):
        res = api_request('POST', '/tickets', {'title': title, 'description': desc, 'priority': prio})
        if res and res.status_code == 201: st.success("Created!")

def main():
    if not st.session_state.token:
        login_page()
    else:
        st.sidebar.write(f"User: {st.session_state.user['username']}")
        page = st.sidebar.radio("Go to", ["Dashboard", "New Ticket"])
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.rerun()
            
        if page == "Dashboard": dashboard()
        if page == "New Ticket": create_ticket()

if __name__ == "__main__":
    main()
