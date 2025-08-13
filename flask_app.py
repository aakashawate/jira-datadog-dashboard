#!/usr/bin/env python3
"""
Flask-based Dashboard Server with Simple Authentication
Migrated from dashboard_server.py with added login functionality
"""

from flask import Flask, render_template, render_template_string, request, session, redirect, url_for, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
import threading
import time
from utils import Logger

# Initialize logger
logger = Logger.get_logger('flask_dashboard')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate secure secret key
app.permanent_session_lifetime = timedelta(hours=2)  # 2-hour session timeout

# Enable CORS
CORS(app)

# Simple user store (replace with database later if needed)
USERS = {
    "jiradd": {
        "password_hash": "b8f57d6d8d5c5c5e5f5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e",  # Will be updated from users.json
        "role": "admin",
        "created_at": "2025-08-13"
    }
}

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session and session.get('authenticated', False)

def load_users_from_file():
    """Load users from users.json file if it exists"""
    global USERS
    try:
        if os.path.exists('users.json'):
            with open('users.json', 'r') as f:
                USERS = json.load(f)
                logger.debug("Users loaded from users.json")
    except Exception as e:
        logger.warning(f"Could not load users.json: {e}")

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    """Redirect to dashboard if authenticated, otherwise to login"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    # Load users from file on each login attempt to get latest data
    load_users_from_file()
    
    # Check for logout message
    logged_out = request.args.get('logged_out')
    logout_message = "You have been logged out successfully." if logged_out else None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if username in USERS and verify_password(password, USERS[username]['password_hash']):
            session['user_id'] = username
            session['user_role'] = USERS[username]['role']
            session['authenticated'] = True
            session['login_time'] = datetime.now().isoformat()
            
            if remember:
                session.permanent = True
            
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password", logout_message=logout_message)
    
    return render_template_string(LOGIN_TEMPLATE, logout_message=logout_message)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    user_id = session.get('user_id', 'unknown')
    session.clear()
    logger.info(f"User {user_id} logged out")
    
    # Add logout message to be displayed on login page
    from flask import flash
    return redirect(url_for('login') + '?logged_out=1')

@app.route('/dashboard')
@require_auth
def dashboard():
    """Main dashboard page"""
    return send_from_directory('.', 'unified_dashboard.html')

@app.route('/api/issues')
@require_auth
def api_issues():
    """API endpoint for issues data"""
    try:
        issues_file = "donation_platform_data/donation_issues.json"
        if os.path.exists(issues_file):
            with open(issues_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Served issues data to {session.get('user_id')}")
            return jsonify(data)
        else:
            logger.error(f"Issues file not found: {issues_file}")
            return jsonify({"error": "Issues data not found"}), 404
    except Exception as e:
        logger.error(f"Error serving issues data: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/project')
@require_auth
def api_project():
    """API endpoint for project data"""
    try:
        project_file = "donation_platform_data/donation_project.json"
        if os.path.exists(project_file):
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Served project data to {session.get('user_id')}")
            return jsonify(data)
        else:
            logger.warning(f"Project file not found: {project_file}")
            return jsonify({"error": "Project data not found"}), 404
    except Exception as e:
        logger.error(f"Error serving project data: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/status')
@require_auth
def api_status():
    """API endpoint for system status"""
    user_info = {
        "user_id": session.get('user_id'),
        "role": session.get('user_role'),
        "login_time": session.get('login_time'),
        "session_permanent": session.permanent
    }
    return jsonify({
        "status": "authenticated",
        "server_time": datetime.now().isoformat(),
        "user": user_info
    })

# Serve static files (CSS, JS, etc.)
@app.route('/<path:filename>')
@require_auth
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

# Login template (embedded for simplicity)
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Dashboard - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .login-header h1 {
            color: #4a5568;
            font-size: 28px;
            margin-bottom: 8px;
        }
        .login-header p {
            color: #718096;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #4a5568;
            font-weight: 500;
        }
        .form-group input[type="text"],
        .form-group input[type="password"] {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        .checkbox-group {
            display: flex;
            align-items: center;
            margin-bottom: 25px;
        }
        .checkbox-group input[type="checkbox"] {
            margin-right: 8px;
        }
        .checkbox-group label {
            font-size: 14px;
            color: #718096;
            margin-bottom: 0;
        }
        .login-btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .login-btn:hover {
            background: #5a67d8;
        }
        .error {
            background: #fed7d7;
            color: #e53e3e;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
        }
        .success {
            background: #c6f6d5;
            color: #22543d;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 14px;
        }
        .credentials {
            margin-top: 25px;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            font-size: 12px;
            color: #4a5568;
        }
        .credentials h4 {
            margin-bottom: 8px;
            color: #2d3748;
        }
        .cred-item {
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>Jira Dashboard</h1>
            <p>Please sign in to access the monitoring dashboard</p>
        </div>
        
        {% if logout_message %}
        <div class="success">{{ logout_message }}</div>
        {% endif %}
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="remember" name="remember">
                <label for="remember">Remember me for 2 hours</label>
            </div>
            
            <button type="submit" class="login-btn">Sign In</button>
        </form>
        
        <div class="credentials">
            <h4>Access Information:</h4>
            <div class="cred-item">Please contact your administrator for login credentials</div>
        </div>
    </div>
</body>
</html>
'''

def start_flask_app(host='127.0.0.1', port=8080, debug=False):
    """Start the Flask application"""
    logger.info(f"Starting Flask dashboard server on {host}:{port}")
    
    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(2)
        logger.info("Opening dashboard in browser...")
        webbrowser.open(f'http://{host}:{port}')
    
    if not debug:
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Check if required files exist
    if not os.path.exists("unified_dashboard.html"):
        print("ERROR: unified_dashboard.html not found in current directory")
        print("INFO: Make sure you're in the jira-issues-fetch directory")
        exit(1)
    
    print("=" * 60)
    print("JIRA DASHBOARD WITH AUTHENTICATION")
    print("=" * 60)
    print(f"Dashboard URL: http://localhost:8080")
    print(f"Please use your assigned credentials to login")
    print(f"Session timeout: 2 hours")
    print("=" * 60)
    
    try:
        start_flask_app(debug=False)
    except KeyboardInterrupt:
        print("\nShutting down Flask dashboard server...")
    except OSError as e:
        if "Address already in use" in str(e):
            print("ERROR: Port 8080 is already in use")
            print("INFO: Stop existing servers with 'python run_pipeline.py --stop'")
        else:
            print(f"ERROR: Server error: {e}")
