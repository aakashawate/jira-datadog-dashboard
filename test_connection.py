#!/usr/bin/env python3
"""
Simple test script to validate Jira connection
"""

import requests
import sys
import json

# Test configuration
JIRA_BASE_URL = "https://tseljira.atlassian.net"
JIRA_EMAIL = "saiakki37@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0T3Z-hQti6F4mZY6wKxYWug2xv5eCem4dCo-LjPe_lpCag3Ph2drfyrGNPgFtEtlHwyosBdA_HUHlOjuJbHJBgpSzfjtKdevFMSjuiq8X-TCfcsH2LBe5sZUvBY8aNnQ0-YzmyZ992txcFg-xZt8lMp2RrFE_e9zUI1VIXIsjDk4=7C06EFA9"

def test_jira_connection():
    """Test basic Jira API connection"""
    print("Testing Jira connection...")
    
    try:
        # Test basic API access
        session = requests.Session()
        session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        
        url = f"{JIRA_BASE_URL}/rest/api/3/myself"
        print(f"Connecting to: {url}")
        
        response = session.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Connection successful!")
            print(f"Logged in as: {user_info.get('displayName', 'Unknown')}")
            print(f"Email: {user_info.get('emailAddress', 'Unknown')}")
            return True
        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_project_access():
    """Test project access"""
    print("\nTesting project access...")
    
    try:
        session = requests.Session()
        session.auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        
        # List all projects to see what's available
        url = f"{JIRA_BASE_URL}/rest/api/3/project"
        print(f"Fetching projects from: {url}")
        
        response = session.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Found {len(projects)} projects:")
            
            for project in projects[:5]:  # Show first 5 projects
                print(f"  - {project.get('key', 'Unknown')} ({project.get('id', 'Unknown')}): {project.get('name', 'Unknown')}")
            
            if len(projects) > 5:
                print(f"  ... and {len(projects) - 5} more")
            
            return projects
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Project access error: {e}")
        return None

if __name__ == "__main__":
    print("Jira Connection Test")
    print("=" * 40)
    
    # Test connection
    if test_jira_connection():
        # Test project access
        projects = test_project_access()
        
        if projects:
            print(f"\n✅ All tests passed!")
            print(f"You have access to {len(projects)} projects.")
            print(f"Update JIRA_PROJECT_ID in the config to use a specific project.")
        else:
            print(f"\n⚠️ Connection works but no project access.")
    else:
        print(f"\n❌ Connection failed. Check your credentials.")
    
    print("\nTest completed.")
