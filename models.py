import bcrypt
from datetime import datetime, timedelta
from config import Config

class User:
    def __init__(self, id, username, email, role, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = password_hash
        self.created_at = created_at
    
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_user(db_manager, username, email, password, role='user'):
        if role not in Config.VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {Config.VALID_ROLES}")
        password_hash = User.hash_password(password)
        # MySQL uses %s placeholder
        query = 'INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)'
        return db_manager.execute_query(query, (username, email, password_hash, role))
    
    @staticmethod
    def get_by_username(db_manager, username):
        query = 'SELECT * FROM users WHERE username = %s'
        row = db_manager.execute_query(query, (username,), fetch_one=True)
        if row:
            return User(row['id'], row['username'], row['email'], row['role'], row['password_hash'], row['created_at'])
        return None

    def to_dict(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'role': self.role, 'created_at': self.created_at}

class Ticket:
    def __init__(self, id, title, description, priority, status, created_by, assigned_to=None, created_at=None, updated_at=None, resolved_at=None, sla_deadline=None):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.created_by = created_by
        self.assigned_to = assigned_to
        self.created_at = created_at
        self.updated_at = updated_at
        self.resolved_at = resolved_at
        self.sla_deadline = sla_deadline
    
    @staticmethod
    def create_ticket(db_manager, title, description, priority, created_by):
        if priority not in Config.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority. Must be one of: {Config.VALID_PRIORITIES}")
        
        created_at = datetime.now()
        sla_hours = Config.SLA_THRESHOLDS.get(priority, 48)
        sla_deadline = created_at + timedelta(hours=sla_hours)
        
        query = 'INSERT INTO tickets (title, description, priority, status, created_by, sla_deadline) VALUES (%s, %s, %s, "open", %s, %s)'
        return db_manager.execute_query(query, (title, description, priority, created_by, sla_deadline))
    
    @staticmethod
    def get_by_id(db_manager, ticket_id):
        query = 'SELECT * FROM tickets WHERE id = %s'
        row = db_manager.execute_query(query, (ticket_id,), fetch_one=True)
        if row:
            return Ticket(row['id'], row['title'], row['description'], row['priority'], row['status'], row['created_by'], row['assigned_to'], row['created_at'], row['updated_at'], row['resolved_at'], row['sla_deadline'])
        return None
    
    @staticmethod
    def get_all_tickets(db_manager, filters=None):
        query = 'SELECT * FROM tickets'
        params = []
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f'{key} = %s')
                params.append(value)
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        query += ' ORDER BY created_at DESC'
        rows = db_manager.execute_query(query, tuple(params), fetch_all=True)
        return [Ticket(row['id'], row['title'], row['description'], row['priority'], row['status'], row['created_by'], row['assigned_to'], row['created_at'], row['updated_at'], row['resolved_at'], row['sla_deadline']) for row in rows]
    
    def update_status(self, db_manager, new_status):
        if new_status not in Config.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {Config.VALID_STATUSES}")
        
        resolved_at = datetime.now() if new_status == 'resolved' else self.resolved_at
        query = 'UPDATE tickets SET status = %s, updated_at = CURRENT_TIMESTAMP, resolved_at = %s WHERE id = %s'
        db_manager.execute_query(query, (new_status, resolved_at, self.id))
        self.status = new_status
        self.resolved_at = resolved_at

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description, 'priority': self.priority,
            'status': self.status, 'created_by': self.created_by, 'assigned_to': self.assigned_to,
            'created_at': self.created_at, 'updated_at': self.updated_at, 'resolved_at': self.resolved_at,
            'sla_deadline': self.sla_deadline
        }
