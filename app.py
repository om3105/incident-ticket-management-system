"""
Flask API for Incident Ticket Management System
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_manager import DBManager
from models import User, Ticket
from auth import generate_token, token_required
from config import Config

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize database
db_manager = DBManager()

# ==================== General Routes ====================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Incident Ticket System API',
        'endpoints': ['/api/auth/register', '/api/auth/login', '/api/tickets', '/api/health']
    }), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy'}), 200

# ==================== Authentication ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        if not all([data.get('username'), data.get('email'), data.get('password')]):
            return jsonify({'error': 'Missing fields'}), 400
        
        User.create_user(db_manager, data['username'], data['email'], data['password'], data.get('role', 'user'))
        return jsonify({'message': 'Registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        user = User.get_by_username(db_manager, data.get('username'))
        
        if not user or not User.verify_password(data.get('password'), user.password_hash):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token(user.id, user.username, user.role)
        return jsonify({'token': token, 'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Ticket Management ====================

@app.route('/api/tickets', methods=['GET'])
@token_required
def get_tickets(current_user):
    """Get all tickets"""
    try:
        filters = {}
        if current_user['role'] == 'user':
            filters['created_by'] = current_user['user_id']
            
        # Apply query filters
        if request.args.get('status'): filters['status'] = request.args.get('status')
        if request.args.get('priority'): filters['priority'] = request.args.get('priority')
        
        tickets = Ticket.get_all_tickets(db_manager, filters)
        return jsonify({'tickets': [t.to_dict() for t in tickets]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
@token_required
def get_ticket(current_user, ticket_id):
    """Get single ticket"""
    try:
        ticket = Ticket.get_by_id(db_manager, ticket_id)
        if not ticket: return jsonify({'error': 'Not found'}), 404
        return jsonify({'ticket': ticket.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets', methods=['POST'])
@token_required
def create_ticket(current_user):
    """Create ticket"""
    try:
        data = request.get_json()
        if not all([data.get('title'), data.get('description')]):
            return jsonify({'error': 'Missing fields'}), 400
            
        Ticket.create_ticket(db_manager, data['title'], data['description'], data.get('priority', 'medium'), current_user['user_id'])
        return jsonify({'message': 'Created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
@token_required
def update_ticket(current_user, ticket_id):
    """Update ticket status"""
    try:
        if current_user['role'] == 'user':
            return jsonify({'error': 'Unauthorized'}), 403
            
        ticket = Ticket.get_by_id(db_manager, ticket_id)
        if not ticket: return jsonify({'error': 'Not found'}), 404
        
        if request.get_json().get('status'):
            ticket.update_status(db_manager, request.get_json()['status'])
            
        return jsonify({'message': 'Updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    db_manager.initialize_database()
    print(f"Server running on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)
