import mysql.connector
from contextlib import contextmanager
from config import Config

class DBManager:
    def __init__(self):
        self.config = {
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'host': Config.MYSQL_HOST,
            'database': Config.MYSQL_DB,
            'raise_on_warnings': False
        }
        print(f"DEBUG: Connecting to MySQL with: {self.config}")
        
    @contextmanager
    def get_connection(self):
        conn = mysql.connector.connect(**self.config)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        # Connect without database to create it if not exists
        init_config = self.config.copy()
        del init_config['database']
        try:
            conn = mysql.connector.connect(**init_config)
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
            conn.close()
        except Exception as e:
            print(f"Error creating database: {e}")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    role ENUM('admin', 'agent', 'user') NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    priority ENUM('low', 'medium', 'high', 'critical') NOT NULL,
                    status ENUM('open', 'in_progress', 'resolved', 'closed') NOT NULL,
                    created_by INT NOT NULL,
                    assigned_to INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL,
                    sla_deadline TIMESTAMP NULL,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    FOREIGN KEY (assigned_to) REFERENCES users(id)
                )
            ''')
            # Indexes are created automatically for foreign keys and primary keys in MySQL
            # Adding specific indexes if needed
            try:
                cursor.execute('CREATE INDEX idx_tickets_status ON tickets(status)')
            except: pass # Index might already exist
            try:
                cursor.execute('CREATE INDEX idx_tickets_priority ON tickets(priority)')
            except: pass
            
            conn.commit()
            print("Database initialized successfully!")
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True) # Return dicts like sqlite3.Row
                cursor.execute(query, params or ())
                if fetch_one: return cursor.fetchone()
                elif fetch_all: return cursor.fetchall()
                else: return cursor.lastrowid
        except mysql.connector.Error as e:
            raise Exception(f"Database error: {str(e)}")
