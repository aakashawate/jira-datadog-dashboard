#!/usr/bin/env python3
"""
Configuration file for Jira Integration Tool

Edit this file to customize your settings without touching the main code.
"""

import os

# ============================================================================
# JIRA CONFIGURATION
# ============================================================================

# Your Jira instance details
JIRA_BASE_URL = "https://tseljira.atlassian.net"
JIRA_EMAIL = "saiakki37@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0T3Z-hQti6F4mZY6wKxYWug2xv5eCem4dCo-LjPe_lpCag3Ph2drfyrGNPgFtEtlHwyosBdA_HUHlOjuJbHJBgpSzfjtKdevFMSjuiq8X-TCfcsH2LBe5sZUvBY8aNnQ0-YzmyZ992txcFg-xZt8lMp2RrFE_e9zUI1VIXIsjDk4=7C06EFA9"

# Project settings
JIRA_PROJECT_ID = "10000"  # Update this to your actual project ID
JIRA_MAX_RESULTS = 100     # Number of issues to fetch per request

# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================

# Storage mode: True for Database, False for File System
USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true'

# File System settings (when USE_DATABASE = False)
DATA_DIR = os.getenv('DATA_DIR', 'data')
BACKUP_RETENTION_DAYS = 30  # How long to keep backups

# Database settings (when USE_DATABASE = True)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USERNAME = os.getenv('DB_USER', 'jira_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_DATABASE = os.getenv('DB_NAME', 'jira_monitoring')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'jira_sync.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# ============================================================================
# FIELD MAPPING (Advanced)
# ============================================================================

# Jira fields to fetch - add custom fields here if needed
JIRA_FIELDS = [
    'id', 'key', 'summary', 'description', 'status', 'priority', 
    'issuetype', 'created', 'updated', 'assignee', 'reporter',
    # Add custom fields like: 'customfield_10001'
]

# Status mappings for statistics
ACTIVE_STATUSES = ['In Progress', 'Open', 'Reopened', 'To Do']
CLOSED_STATUSES = ['Closed', 'Resolved', 'Done', 'Cancelled']

# ============================================================================
# QUICK SETUP HELPERS
# ============================================================================

def get_project_url():
    """Get the Jira project URL for easy access"""
    return f"{JIRA_BASE_URL}/browse/{JIRA_PROJECT_ID}"

def validate_config():
    """Basic configuration validation"""
    issues = []
    
    if "YOUR_" in JIRA_BASE_URL:
        issues.append("JIRA_BASE_URL needs to be updated")
    
    if "YOUR_" in JIRA_EMAIL:
        issues.append("JIRA_EMAIL needs to be updated")
    
    if "YOUR_" in JIRA_API_TOKEN:
        issues.append("JIRA_API_TOKEN needs to be updated")
    
    if USE_DATABASE and "your_password" in DB_PASSWORD:
        issues.append("DB_PASSWORD needs to be updated for database mode")
    
    return issues

if __name__ == "__main__":
    # Quick config check
    print("Jira Integration Configuration")
    print("=" * 40)
    print(f"Jira URL: {JIRA_BASE_URL}")
    print(f"Project ID: {JIRA_PROJECT_ID}")
    print(f"Storage Mode: {'Database' if USE_DATABASE else 'File System'}")
    print(f"Project URL: {get_project_url()}")
    
    issues = validate_config()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration looks good!")
