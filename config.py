import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'incident_tickets'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_EXPIRATION = timedelta(hours=24)
    
    SLA_THRESHOLDS = {'critical': 4, 'high': 8, 'medium': 24, 'low': 48}
    VALID_STATUSES = ['open', 'in_progress', 'resolved', 'closed']
    VALID_PRIORITIES = ['low', 'medium', 'high', 'critical']
    VALID_ROLES = ['admin', 'agent', 'user']
    
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5001
    FLASK_DEBUG = True
