import mysql.connector
import sqlite3
import os
from contextlib import contextmanager
from config import Config

class DBManager:
    def __init__(self):
        self.db_type = Config.DB_TYPE
        if self.db_type == 'mysql':
            self.config = {
                'user': Config.MYSQL_USER,
                'password': Config.MYSQL_PASSWORD,
                'host': Config.MYSQL_HOST,
                'database': Config.MYSQL_DB,
                'raise_on_warnings': False
            }
            print(f"DEBUG: Connecting to MySQL with: {self.config}")
        else:
            self.db_path = Config.SQLITE_DB
            print(f"DEBUG: Connecting to SQLite: {self.db_path}")
        
    @contextmanager
    def get_connection(self):
        if self.db_type == 'mysql':
            conn = mysql.connector.connect(**self.config)
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # Access columns by name
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    def initialize_database(self):
        if self.db_type == 'mysql':
            self._init_mysql()
        else:
            self._init_sqlite()

    def _init_mysql(self):
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
            try:
                cursor.execute('CREATE INDEX idx_tickets_status ON tickets(status)')
            except: pass 
            try:
                cursor.execute('CREATE INDEX idx_tickets_priority ON tickets(priority)')
            except: pass
            
            conn.commit()
            print("MySQL Database initialized successfully!")

    def _init_sqlite(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # SQLite doesn't have ENUM, use CHECK constraints or just TEXT.
            # SQLite AUTO_INCREMENT is implicit with INTEGER PRIMARY KEY
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'agent', 'user')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'critical')),
                    status TEXT NOT NULL CHECK(status IN ('open', 'in_progress', 'resolved', 'closed')),
                    created_by INTEGER NOT NULL,
                    assigned_to INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL,
                    sla_deadline TIMESTAMP NULL,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    FOREIGN KEY (assigned_to) REFERENCES users(id)
                )
            ''')
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)')
            
            conn.commit()
            print("SQLite Database initialized successfully!")
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        # Adapter for placeholders
        if self.db_type != 'mysql':
            query = query.replace('%s', '?')
            
        try:
            with self.get_connection() as conn:
                if self.db_type == 'mysql':
                    cursor = conn.cursor(dictionary=True)
                else:
                    cursor = conn.cursor() # connection has row_factory set
                
                cursor.execute(query, params or ())
                
                if fetch_one:
                    if self.db_type == 'mysql': return cursor.fetchone()
                    else: 
                        row = cursor.fetchone()
                        return dict(row) if row else None
                elif fetch_all:
                    if self.db_type == 'mysql': return cursor.fetchall()
                    else: return [dict(row) for row in cursor.fetchall()]
                else: 
                    return cursor.lastrowid
        except (mysql.connector.Error, sqlite3.Error) as e:
            raise Exception(f"Database error: {str(e)}")
