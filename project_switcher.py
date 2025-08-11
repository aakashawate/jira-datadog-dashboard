#!/usr/bin/env python3
"""
Project switcher for Jira Integration Tool
Allows easy switching between different projects
"""

import os
import sys
import json

# Available projects (discovered from test_connection.py)
PROJECTS = {
    "donation": {
        "id": "10000",
        "key": "DP", 
        "name": "Donation Platform"
    },
    "support": {
        "id": "10001",
        "key": "SUP",
        "name": "Support"
    }
}

def show_projects():
    """Show available projects"""
    print("Available Projects:")
    print("-" * 40)
    for alias, project in PROJECTS.items():
        print(f"  {alias:10} -> {project['key']} ({project['id']}): {project['name']}")

def sync_project(project_alias, storage_mode=None):
    """Sync a specific project"""
    if project_alias not in PROJECTS:
        print(f"❌ Unknown project: {project_alias}")
        show_projects()
        return False
    
    project = PROJECTS[project_alias]
    print(f"🔄 Syncing project: {project['name']} ({project['key']})")
    
    # Import and configure
    import jira_integration
    jira_integration.Config.JIRA_PROJECT_ID = project['id']
    
    if storage_mode == 'database':
        jira_integration.Config.USE_DATABASE = True
        print("📁 Using Database storage")
    elif storage_mode == 'filesystem':
        jira_integration.Config.USE_DATABASE = False
        print("📁 Using File System storage")
    
    # Run sync
    try:
        jira_integration.main()
        return True
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        return False

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Jira Project Switcher")
        print("=" * 40)
        print("Usage:")
        print("  python project_switcher.py <project> [storage_mode]")
        print("")
        print("Examples:")
        print("  python project_switcher.py donation")
        print("  python project_switcher.py support filesystem")
        print("  python project_switcher.py donation database")
        print("")
        show_projects()
        return
    
    project_alias = sys.argv[1].lower()
    storage_mode = sys.argv[2].lower() if len(sys.argv) > 2 else None
    
    if project_alias in ['list', 'projects']:
        show_projects()
        return
    
    success = sync_project(project_alias, storage_mode)
    if success:
        print("✅ Sync completed successfully!")
    else:
        print("❌ Sync failed!")

if __name__ == "__main__":
    main()
