#!/usr/bin/env python3
"""
Authentication-enabled Dashboard Launcher
Modified from dashboard_server.py to use Flask with authentication
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from utils import Logger

# Initialize logger
logger = Logger.get_logger('auth_dashboard')

def check_data_files():
    """Check if required data files exist"""
    issues_file = "donation_platform_data/donation_issues.json"
    project_file = "donation_platform_data/donation_project.json"
    
    print("Checking data files...")
    
    if not os.path.exists(issues_file):
        print(f"ERROR: Jira issues data not found: {issues_file}")
        print(f"INFO: Run 'python jira_integration.py' first to fetch Jira data")
        return False
    
    if not os.path.exists(project_file):
        print(f"⚠️  Project data not found: {project_file}")
        print(f"💡 Run 'python jira_integration.py' first to fetch project data")
    
    # Check if data is recent
    try:
        with open(issues_file, 'r') as f:
            data = json.load(f)
        
        last_updated = data.get('last_updated', 'Unknown')
        total_issues = data.get('total_issues', 0)
        
        print(f"SUCCESS: Found Jira data:")
        print(f"   Total Issues: {total_issues}")
        print(f"   Last Updated: {last_updated}")
        print(f"   File: {issues_file}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error reading Jira data: {e}")
        return False

def setup_authentication():
    """Setup authentication if not already configured"""
    users_file = "users.json"
    
    if not os.path.exists(users_file):
        print("Setting up authentication for first time...")
        
        # Create default users file with secure credentials
        import hashlib
        
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
        
        default_users = {
            "jiradd": {
                "password_hash": hash_password("JiraDD@25!"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        
        with open(users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        print(f"✅ Authentication configured with admin user")
        print(f"   Username: jiradd")
        print(f"   Use 'python user_manager.py' to manage users")
        print(f"   ⚠️  Keep your credentials secure!")

def main():
    """Main function"""
    print("=" * 60)
    print("JIRA DASHBOARD WITH AUTHENTICATION")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("unified_dashboard.html"):
        print("ERROR: Dashboard file not found in current directory")
        print("INFO: Make sure you're in the jira-issues-fetch directory")
        return
    
    # Setup authentication
    setup_authentication()
    
    # Check data files
    if not check_data_files():
        print("\nAttempting to fetch fresh Jira data...")
        try:
            # Use virtual environment Python if available
            venv_python = Path(".venv/Scripts/python.exe")
            if venv_python.exists():
                subprocess.run([str(venv_python), "jira_integration.py"], check=True)
            else:
                subprocess.run([sys.executable, "jira_integration.py"], check=True)
            print("SUCCESS: Jira data updated")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to update Jira data: {e}")
            print("INFO: Please run 'python jira_integration.py' manually")
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Starting authenticated Flask dashboard...")
    print("Dashboard URL: http://localhost:8080")
    print("Login with your assigned credentials")
    print("User management: python user_manager.py")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the Flask app
    try:
        # Use virtual environment Python if available
        venv_python = Path(".venv/Scripts/python.exe")
        if venv_python.exists():
            subprocess.run([str(venv_python), "flask_app.py"])
        else:
            subprocess.run([sys.executable, "flask_app.py"])
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
    except OSError as e:
        if "Address already in use" in str(e):
            print("ERROR: Port 8080 is already in use")
            print("INFO: Try stopping existing servers first")
        else:
            print(f"ERROR: Server error: {e}")

if __name__ == "__main__":
    main()
