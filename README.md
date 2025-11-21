# Incident Ticket Management System
### Final Year Project (2025)

## 🎓 Abstract
The **Incident Ticket Management System** is a comprehensive software solution designed to streamline the process of reporting, tracking, and resolving IT incidents within an organization. This project aims to replace manual tracking methods with a digital, automated system that ensures accountability and efficiency. It features role-based access control, real-time SLA monitoring, and detailed reporting capabilities.

## 🚀 Features
- **User Authentication**: Secure login and registration system with role-based access (User, Agent, Admin).
- **Ticket Management**: Users can create tickets; Agents can view and resolve them.
- **SLA Monitoring**: Automated tracking of Service Level Agreements to ensure timely resolution.
- **Reporting Dashboard**: Visual statistics and downloadable reports (CSV/JSON) for Admins.
- **REST API**: A robust backend API built with Flask.
- **Interactive UI**: A user-friendly frontend built with Streamlit.

## 🛠️ Tech Stack Used
- **Language**: Python 3.12
- **Backend Framework**: Flask (Microframework)
- **Frontend Framework**: Streamlit
- **Database**: SQLite (Lightweight Relational Database)
- **Authentication**: JWT (JSON Web Tokens)
- **Libraries**: Pandas (Data Analysis), Requests (HTTP Client)

## 💻 How to Run the Project

### Prerequisites
- Python 3.x installed on your system.

### Steps
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Backend Server**:
    Open a terminal and run:
    ```bash
    python3 app.py
    ```

3.  **Start the Frontend Application**:
    Open a **new** terminal and run:
    ```bash
    streamlit run streamlit_app.py
    ```

4.  **Access the App**:
    Open your browser and go to the URL shown (usually `http://localhost:8501`).

## 👨‍💻 Developer Info
**Name**: [Your Name Here]
**Course**: B.Tech Computer Science
**Year**: Final Year
