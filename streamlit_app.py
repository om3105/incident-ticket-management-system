import streamlit as st
import pandas as pd
from db_manager import DBManager
from models import User, Ticket
from config import Config

# Initialize Database
@st.cache_resource
def get_db_manager():
    db = DBManager()
    db.initialize_database()
    return db

db_manager = get_db_manager()

if 'user' not in st.session_state:
    st.session_state.user = None

def login_page():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = User.get_by_username(db_manager, username)
        if user and User.verify_password(password, user.password_hash):
            st.session_state.user = user.to_dict()
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.header("Register")
    new_user = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_pass = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["user", "agent", "admin"])
    if st.button("Register"):
        try:
            User.create_user(db_manager, new_user, new_email, new_pass, role)
            st.success("Registered! Please login.")
        except Exception as e:
            st.error(f"Error: {e}")

def dashboard():
    st.header("Dashboard")
    
    # Filters
    status = st.selectbox("Filter Status", ["All"] + Config.VALID_STATUSES)
    priority = st.selectbox("Filter Priority", ["All"] + Config.VALID_PRIORITIES)
    
    # Build filters
    filters = {}
    if st.session_state.user['role'] == 'user':
        filters['created_by'] = st.session_state.user['id']
        
    if status != "All": filters['status'] = status
    if priority != "All": filters['priority'] = priority
    
    # Fetch tickets
    try:
        tickets = Ticket.get_all_tickets(db_manager, filters)
        if tickets:
            data = [t.to_dict() for t in tickets]
            df = pd.DataFrame(data)
            # Reorder columns for better view
            cols = ['id', 'title', 'priority', 'status', 'created_at']
            if 'assignee' in df.columns: cols.append('assignee')
            st.dataframe(df[cols] if set(cols).issubset(df.columns) else df)
            
            # Ticket Details & Update
            st.divider()
            st.subheader("Ticket Details")
            tid = st.number_input("Enter Ticket ID to view/edit", min_value=1, step=1)
            
            if tid:
                ticket = Ticket.get_by_id(db_manager, tid)
                if ticket:
                    # Access Control for detail view (User can see their own, Agents/Admins all)
                    if st.session_state.user['role'] == 'user' and ticket.created_by != st.session_state.user['id']:
                        st.error("You don't have permission to view this ticket.")
                    else:
                        st.write(f"**Title:** {ticket.title}")
                        st.write(f"**Description:** {ticket.description}")
                        st.write(f"**Status:** {ticket.status} | **Priority:** {ticket.priority}")
                        st.write(f"**Created At:** {ticket.created_at}")
                        
                        # Update Status (Agents/Admins only)
                        if st.session_state.user['role'] in ['agent', 'admin']:
                            st.write("---")
                            new_stat = st.selectbox("Update Status", Config.VALID_STATUSES, index=Config.VALID_STATUSES.index(ticket.status))
                            if st.button("Update Status"):
                                ticket.update_status(db_manager, new_stat)
                                st.success("Status updated!")
                                st.rerun()
                else:
                    st.warning("Ticket not found.")
        else:
            st.info("No tickets found.")
            
    except Exception as e:
        st.error(f"Error fetching tickets: {e}")

def create_ticket():
    st.header("New Ticket")
    title = st.text_input("Title")
    desc = st.text_area("Description")
    prio = st.selectbox("Priority", Config.VALID_PRIORITIES)
    
    if st.button("Submit Ticket"):
        if title and desc:
            try:
                Ticket.create_ticket(db_manager, title, desc, prio, st.session_state.user['id'])
                st.success("Ticket created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please fill in all fields.")

def main():
    if not st.session_state.user:
        login_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.user['username']}")
        st.sidebar.write(f"Role: {st.session_state.user['role']}")
        
        page = st.sidebar.radio("Navigation", ["Dashboard", "New Ticket"])
        
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()
            
        if page == "Dashboard":
            dashboard()
        elif page == "New Ticket":
            create_ticket()

if __name__ == "__main__":
    main()
