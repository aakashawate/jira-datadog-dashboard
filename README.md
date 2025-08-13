# Jira-DataDog Live Monitoring Dashboard

A professional live monitoring system that integrates Jira issues with DataDog dashboard visualization. This system provides real-time tracking of Jira issues with **secure authentication**, automatic data refresh, clean web interface, and comprehensive production-ready logging.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Features](#features)
- [Architecture](#architecture)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Production Deployment](#production-deployment)
- [User Management](#user-management)
- [Troubleshooting](#troubleshooting)

## 🏗️ System Overview

### Purpose
Live monitoring dashboard for Jira issues with integrated DataDog metrics visualization. The system fetches fresh Jira data every 5 minutes and displays it in a responsive web interface with **secure authentication** and comprehensive logging for production deployment.

### Key Components
- **🔐 Authentication System**: Secure login with session management
- **📊 Jira Integration**: Fetches live issue data from Jira API
- **💾 Data Storage**: File-based storage with automatic backups
- **🌐 Live Dashboard**: Web server with auto-refresh capabilities
- **⚙️ Configuration Management**: Centralized configuration system
- **📋 Logging System**: Production-ready logging with rotation and monitoring

## 🚀 Quick Start

### **Start the Complete System (Recommended)**
```bash
# Start with authentication (default)
python run_pipeline.py

# Access at: http://localhost:8080
# Login: jiradd / JiraDD@25!
```

### **Alternative Modes**
```bash
# Legacy mode without authentication
python run_pipeline.py --no-auth

# Dashboard only (use existing data)
python run_pipeline.py --quick-start

# Stop all servers
python run_pipeline.py --stop
```

## 🔐 Authentication

### **Security Features**
- ✅ **Login/Logout System**: Secure session-based authentication
- ✅ **Password Hashing**: SHA-256 encryption
- ✅ **Session Management**: 2-hour timeout with "remember me"
- ✅ **Role-Based Access**: Admin and Viewer roles
- ✅ **Protected Endpoints**: All API routes require authentication

### **Default Login**
- **Username**: `jiradd`
- **Password**: `JiraDD@25!`
- **Role**: `admin`

### **Login Interface**
- Beautiful, responsive login page
- Logout confirmation and proper session cleanup
- Professional security messaging (no credential hints)

## ✨ Features

### **Core Features**
- 🔐 **Secure Authentication**: Login system with session management
- 📊 **Live Data Fetching**: Fresh Jira data every 5 minutes
- 🌐 **Web Dashboard**: Responsive HTML interface at `localhost:8080`
- 🔄 **Auto-Refresh**: Background data updates without manual intervention
- 📈 **DataDog Integration**: Embedded DataDog dashboard iframe
- 🛡️ **Error Recovery**: Graceful handling of API failures

### **Dashboard Features**
- 📊 **Issue Statistics**: Count by status (To Do, In Progress, In Review, Done)
- ⏱️ **Real-time Updates**: Automatic data refresh with cache-busting
- 📱 **Responsive Design**: Works on desktop and mobile browsers
- 🎨 **Status Visualization**: Color-coded issue status indicators
- 🚪 **Logout Button**: Easy and secure logout functionality

### **Technical Features**
- 🔧 **Modular Design**: Reusable components
- ⚙️ **Configuration Management**: Centralized settings
- 📋 **Logging System**: Comprehensive error and info logging
- 💾 **Backup System**: Automatic data backups
- 🖥️ **Cross-Platform**: Works on Windows, Linux, Mac

## 🏛️ Architecture

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄───│  🔐 Flask App   │◄───│  Authentication │
│   (localhost)   │    │  with Auth      │    │     System      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jira API      │◄───│  Integration    │────►│  Data Storage   │
│   (External)    │    │     Layer       │    │  (JSON Files)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Auto-Refresh    │
                       │ System (5 min)  │
                       └─────────────────┘
```

### **Code Structure**
```
├── run_pipeline.py           # 🚀 Main entry point (with auth integration)
├── flask_app.py             # 🔐 Flask application with authentication
├── user_manager.py          # 👥 User management utility
├── config.py                # ⚙️ Centralized configuration
├── jira_integration.py      # 📊 Jira API client and data processing
├── dashboard_server.py      # 🌐 Legacy server (no auth)
├── unified_dashboard.html   # 🎨 Frontend dashboard interface
├── users.json              # 👤 User storage (auto-created)
├── requirements.txt         # 📦 Python dependencies
└── README.md               # 📖 This documentation
```

## ⚙️ Setup & Installation

### **Prerequisites**
- Python 3.8+ 
- Git
- Windows/Linux/Mac

### **Installation Steps**
```bash
# 1. Clone repository
git clone <your-repository-url>
cd jira-issues-fetch

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure Jira credentials
# Edit config.py with your Jira details

# 6. Start the system
python run_pipeline.py
```

### **First Run**
1. The system will automatically create authentication setup
2. Open browser to: http://localhost:8080
3. Login with: `jiradd` / `JiraDD@25!`
4. Dashboard will load with live Jira data

## 🔧 Configuration

### **Jira Configuration (config.py)**
```python
# Your Jira instance details
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"
JIRA_PROJECT_ID = "10000"  # Your project ID
```

### **Authentication Configuration**
- Default user is created automatically
- Users stored in `users.json` file
- Session timeout: 2 hours
- Password hashing: SHA-256

## 🚀 Production Deployment

### **Linux Server Setup**
```bash
# 1. Clone and setup
git clone <your-repo>
cd jira-issues-fetch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure Jira credentials
nano config.py

# 3. Test the system
python run_pipeline.py --quick-start

# 4. Create systemd service
sudo nano /etc/systemd/system/jira-monitor.service
```

### **Systemd Service File**
```ini
[Unit]
Description=Jira Live Monitoring System with Authentication
After=network.target

[Service]
Type=simple
User=jira-monitor
WorkingDirectory=/opt/jira-monitor
Environment=PATH=/opt/jira-monitor/.venv/bin
ExecStart=/opt/jira-monitor/.venv/bin/python run_pipeline.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Start Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable jira-monitor
sudo systemctl start jira-monitor
sudo systemctl status jira-monitor
```

## 👥 User Management

### **Add/Manage Users**
```bash
# Open user management tool
python user_manager.py

# Options available:
# 1. List users
# 2. Add user
# 3. Delete user
# 4. Change password
# 5. Initialize default users
```

### **Programmatic User Management**
```python
# Add user via script
python -c "
import json, hashlib
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load existing users
with open('users.json', 'r') as f:
    users = json.load(f)

# Add new user
users['newuser'] = {
    'password_hash': hash_password('SecurePass123!'),
    'role': 'viewer',
    'created_at': datetime.now().isoformat()
}

# Save users
with open('users.json', 'w') as f:
    json.dump(users, f, indent=2)

print('User added successfully')
"
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **1. Authentication Issues**
```bash
# Reset to default user
python -c "
import json, hashlib
from datetime import datetime

users = {
    'jiradd': {
        'password_hash': hashlib.sha256('JiraDD@25!'.encode()).hexdigest(),
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    }
}

with open('users.json', 'w') as f:
    json.dump(users, f, indent=2)
print('Default user restored: jiradd / JiraDD@25!')
"
```

#### **2. Port Already in Use**
```bash
# Stop existing servers
python run_pipeline.py --stop

# Or find and kill process
netstat -ano | findstr :8080  # Windows
lsof -ti:8080 | xargs kill   # Linux/Mac
```

#### **3. Virtual Environment Issues**
```bash
# Recreate virtual environment
rmdir /s .venv  # Windows
rm -rf .venv    # Linux/Mac

python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

#### **4. Jira Connection Issues**
```bash
# Test Jira connection
python -c "
from jira_integration import JiraClient
client = JiraClient()
print('Connection test:', client.validate_connection())
"
```

#### **5. No Data Displayed**
```bash
# Refresh Jira data
python jira_integration.py

# Check data files
ls donation_platform_data/  # Linux/Mac
dir donation_platform_data\  # Windows
```

### **Log Analysis**
```bash
# Monitor all logs
tail -f logs/*.log  # Linux/Mac
Get-Content logs\*.log -Wait  # Windows

# Check specific components
tail -f logs/flask_dashboard.log
tail -f logs/jira_integration.log
tail -f logs/pipeline.log
```

### **Production Troubleshooting**
```bash
# Check service status
sudo systemctl status jira-monitor

# View service logs
sudo journalctl -u jira-monitor -f

# Restart service
sudo systemctl restart jira-monitor
```

## 📊 API Endpoints (Authentication Required)

### **Available Endpoints**
```
GET  /                    # Redirect to dashboard (auth required)
GET  /login              # Login page
POST /login              # Process login
GET  /logout             # Logout and clear session
GET  /dashboard          # Main dashboard (auth required)
GET  /api/issues         # Jira issues JSON (auth required)
GET  /api/project        # Project data JSON (auth required)
GET  /api/status         # System status (auth required)
```

### **Session Management**
- Session timeout: 2 hours
- Remember me: Extends session
- Automatic logout: On browser close (optional)
- CSRF protection: Built-in with Flask

## 🔒 Security Notes

### **Production Security**
1. **Change Default Password**: Use `python user_manager.py`
2. **Secure users.json**: `chmod 600 users.json`
3. **Use HTTPS**: Add nginx reverse proxy
4. **Firewall**: Restrict port 8080 access
5. **Monitor Logs**: Check for failed login attempts

### **Security Features**
- ✅ Password hashing (SHA-256)
- ✅ Session management with timeout
- ✅ Protected API endpoints
- ✅ Input validation
- ✅ No credential exposure in UI
- ✅ Secure session cookies

## 📞 Support

### **Getting Help**
1. Check this README for common solutions
2. Review log files for error details: `logs/`
3. Test individual components in isolation
4. Verify Jira API connectivity and credentials
5. Use `python user_manager.py` for user issues

### **Development & Contribution**
- **Repository**: [Your GitHub Repository]
- **Issues**: Report bugs via GitHub Issues
- **Documentation**: This README contains all necessary information

---

**System Status**: ✅ Production Ready with Authentication  
**Last Updated**: August 13, 2025  
**Version**: 2.0.0 (With Authentication)  
**Default Login**: jiradd / JiraDD@25!
