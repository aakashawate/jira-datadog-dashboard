#!/usr/bin/env python3
"""
User Management Utility for Jira Dashboard
Simple script to manage users for the authentication system
"""

import json
import hashlib
import getpass
import os
from datetime import datetime

USERS_FILE = "users.json"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def add_user():
    """Add a new user"""
    users = load_users()
    
    print("\n=== Add New User ===")
    username = input("Username: ").strip()
    
    if username in users:
        print(f"Error: User '{username}' already exists!")
        return
    
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("Error: Passwords do not match!")
        return
    
    if len(password) < 4:
        print("Error: Password must be at least 4 characters!")
        return
    
    print("Roles: admin, viewer")
    role = input("Role [viewer]: ").strip() or "viewer"
    
    if role not in ["admin", "viewer"]:
        print("Error: Role must be 'admin' or 'viewer'")
        return
    
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    print(f"✅ User '{username}' added successfully with role '{role}'")

def delete_user():
    """Delete a user"""
    users = load_users()
    
    if not users:
        print("No users found!")
        return
    
    print("\n=== Delete User ===")
    print("Existing users:", ", ".join(users.keys()))
    username = input("Username to delete: ").strip()
    
    if username not in users:
        print(f"Error: User '{username}' not found!")
        return
    
    confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ")
    if confirm.lower() == 'yes':
        del users[username]
        save_users(users)
        print(f"✅ User '{username}' deleted successfully")
    else:
        print("Delete cancelled")

def list_users():
    """List all users"""
    users = load_users()
    
    if not users:
        print("No users found!")
        return
    
    print("\n=== User List ===")
    print(f"{'Username':<15} {'Role':<10} {'Created':<20}")
    print("-" * 45)
    
    for username, data in users.items():
        created = data.get('created_at', 'Unknown')[:19]  # Truncate timestamp
        print(f"{username:<15} {data.get('role', 'viewer'):<10} {created:<20}")

def change_password():
    """Change user password"""
    users = load_users()
    
    if not users:
        print("No users found!")
        return
    
    print("\n=== Change Password ===")
    print("Existing users:", ", ".join(users.keys()))
    username = input("Username: ").strip()
    
    if username not in users:
        print(f"Error: User '{username}' not found!")
        return
    
    password = getpass.getpass("New password: ")
    password_confirm = getpass.getpass("Confirm new password: ")
    
    if password != password_confirm:
        print("Error: Passwords do not match!")
        return
    
    if len(password) < 4:
        print("Error: Password must be at least 4 characters!")
        return
    
    users[username]["password_hash"] = hash_password(password)
    save_users(users)
    print(f"✅ Password changed for user '{username}'")

def initialize_default_users():
    """Initialize with default admin user"""
    users = load_users()
    
    if not users:
        print("No users found. Creating default admin user...")
        users["admin"] = {
            "password_hash": hash_password("admin"),
            "role": "admin",
            "created_at": datetime.now().isoformat()
        }
        save_users(users)
        print("✅ Default admin user created (username: admin, password: admin)")
        print("⚠️  Please change the default password in production!")

def main():
    """Main menu"""
    while True:
        print("\n" + "=" * 50)
        print("JIRA DASHBOARD - USER MANAGEMENT")
        print("=" * 50)
        print("1. List users")
        print("2. Add user")
        print("3. Delete user")
        print("4. Change password")
        print("5. Initialize default users")
        print("6. Exit")
        print("-" * 50)
        
        choice = input("Choose an option (1-6): ").strip()
        
        try:
            if choice == "1":
                list_users()
            elif choice == "2":
                add_user()
            elif choice == "3":
                delete_user()
            elif choice == "4":
                change_password()
            elif choice == "5":
                initialize_default_users()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-6.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
