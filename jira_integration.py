#!/usr/bin/env python3
"""
Jira to Database Integration

Complete integration solution for syncing Jira issues to MySQL database.
Includes configuration, database operations, Jira API client, and main execution.

Author: Development Team
Version: 1.0
"""

import os
import mysql.connector
import requests
import logging
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration settings"""
    
    # ============================================================================
    # UPDATE THESE CREDENTIALS FOR YOUR SERVER
    # ============================================================================
    
    # Jira Configuration
    JIRA_BASE_URL = "YOUR_JIRA_URL"           # e.g., "https://yourcompany.atlassian.net"
    JIRA_EMAIL = "YOUR_EMAIL"                 # e.g., "user@company.com"
    JIRA_API_TOKEN = "YOUR_API_TOKEN"         # Generate from Jira settings
    JIRA_PROJECT_ID = "YOUR_PROJECT_ID"       # e.g., "10000"
    JIRA_MAX_RESULTS = 100
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'YOUR_DB_HOST')           # e.g., 'localhost'
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USERNAME = os.getenv('DB_USER', 'YOUR_DB_USER')       # e.g., 'jira_user'
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'YOUR_DB_PASSWORD')   # Your database password
    DB_DATABASE = os.getenv('DB_NAME', 'YOUR_DB_NAME')       # e.g., 'jira_monitoring'

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

class Database:
    """Database operations for MySQL"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USERNAME,
                password=Config.DB_PASSWORD,
                database=Config.DB_DATABASE,
                charset='utf8mb4'
            )
            logger.info("Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def init_tables(self):
        """Create database tables if they don't exist"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jira_projects (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                key_name VARCHAR(50) NOT NULL,
                project_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jira_issues (
                id VARCHAR(50) PRIMARY KEY,
                project_id VARCHAR(50),
                issue_key VARCHAR(50) NOT NULL,
                summary TEXT,
                description TEXT,
                status VARCHAR(100),
                priority VARCHAR(50),
                issue_type VARCHAR(100),
                created_date DATETIME,
                updated_date DATETIME,
                assignee VARCHAR(255),
                reporter VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES jira_projects(id)
            )
        """)
        
        self.connection.commit()
        cursor.close()
        logger.info("Database tables initialized")
        return True
    
    def save_issues(self, project_data, issues_data):
        """Save project and issues to database"""
        if not self.connection:
            return False
            
        cursor = self.connection.cursor()
        
        try:
            # Save project
            cursor.execute("""
                INSERT INTO jira_projects (id, name, key_name, project_type)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                key_name = VALUES(key_name),
                project_type = VALUES(project_type)
            """, (
                project_data['id'],
                project_data['name'],
                project_data['key'],
                project_data.get('projectTypeKey', 'unknown')
            ))
            
            # Save issues
            for issue in issues_data:
                cursor.execute("""
                    INSERT INTO jira_issues (
                        id, project_id, issue_key, summary, description,
                        status, priority, issue_type, created_date, updated_date,
                        assignee, reporter
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        summary = VALUES(summary),
                        description = VALUES(description),
                        status = VALUES(status),
                        priority = VALUES(priority),
                        issue_type = VALUES(issue_type),
                        updated_date = VALUES(updated_date),
                        assignee = VALUES(assignee),
                        reporter = VALUES(reporter)
                """, (
                    issue['id'],
                    project_data['id'],
                    issue['key'],
                    issue.get('summary', ''),
                    issue.get('description', ''),
                    issue.get('status', ''),
                    issue.get('priority', ''),
                    issue.get('issuetype', ''),
                    issue.get('created'),
                    issue.get('updated'),
                    issue.get('assignee', ''),
                    issue.get('reporter', '')
                ))
            
            self.connection.commit()
            logger.info(f"Saved {len(issues_data)} issues to database")
            return True
            
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to save to database: {e}")
            return False
        finally:
            cursor.close()
    
    def get_stats(self):
        """Get project statistics from database"""
        if not self.connection:
            return None
            
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_issues,
                    SUM(CASE WHEN status IN ('In Progress', 'Open', 'Reopened') THEN 1 ELSE 0 END) as active_issues,
                    SUM(CASE WHEN status IN ('Closed', 'Resolved', 'Done') THEN 1 ELSE 0 END) as closed_issues,
                    SUM(CASE WHEN status = 'To Do' THEN 1 ELSE 0 END) as todo_issues
                FROM jira_issues
            """)
            
            stats = cursor.fetchone()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return None
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# ============================================================================
# JIRA CLIENT
# ============================================================================

class JiraClient:
    """Jira API client for fetching project and issue data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.auth = (Config.JIRA_EMAIL, Config.JIRA_API_TOKEN)
        
    def get_project(self):
        """Get project details"""
        url = f"{Config.JIRA_BASE_URL}/rest/api/3/project/{Config.JIRA_PROJECT_ID}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None
    
    def get_all_issues(self):
        """Get all issues from the project"""
        issues = []
        start_at = 0
        
        while True:
            url = f"{Config.JIRA_BASE_URL}/rest/api/3/search"
            params = {
                'jql': f'project = {Config.JIRA_PROJECT_ID}',
                'startAt': start_at,
                'maxResults': Config.JIRA_MAX_RESULTS,
                'fields': 'id,key,summary,description,status,priority,issuetype,created,updated,assignee,reporter'
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                batch_issues = []
                for issue in data['issues']:
                    processed = {
                        'id': issue['id'],
                        'key': issue['key'],
                        'summary': issue['fields'].get('summary', ''),
                        'description': issue['fields'].get('description', ''),
                        'status': issue['fields']['status']['name'] if issue['fields'].get('status') else '',
                        'priority': issue['fields']['priority']['name'] if issue['fields'].get('priority') else '',
                        'issuetype': issue['fields']['issuetype']['name'] if issue['fields'].get('issuetype') else '',
                        'created': self._parse_date(issue['fields'].get('created')),
                        'updated': self._parse_date(issue['fields'].get('updated')),
                        'assignee': issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else '',
                        'reporter': issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else ''
                    }
                    batch_issues.append(processed)
                
                issues.extend(batch_issues)
                logger.info(f"Fetched {len(batch_issues)} issues (total: {len(issues)})")
                
                if len(data['issues']) < Config.JIRA_MAX_RESULTS:
                    break
                    
                start_at += Config.JIRA_MAX_RESULTS
                
            except Exception as e:
                logger.error(f"Failed to fetch issues: {e}")
                break
        
        return issues
    
    def _parse_date(self, date_str):
        """Parse Jira date string to datetime"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

# ============================================================================
# DATABASE SETUP UTILITY
# ============================================================================

def setup_database():
    """Setup database and user for Jira integration"""
    
    # Configuration for database setup
    DB_ROOT_PASSWORD = input("Enter MySQL root password: ")
    
    try:
        # Connect as root
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user='root',
            password=DB_ROOT_PASSWORD
        )
        cursor = connection.cursor()
        
        print("Creating database...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_DATABASE}")
        
        print("Creating user...")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{Config.DB_USERNAME}'@'%' IDENTIFIED BY '{Config.DB_PASSWORD}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {Config.DB_DATABASE}.* TO '{Config.DB_USERNAME}'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("Database setup completed successfully!")
        print(f"Database: {Config.DB_DATABASE}")
        print(f"User: {Config.DB_USERNAME}")
        print("Update the Config class with your actual credentials")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Setup failed: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jira_sync.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main synchronization function"""
    logger.info("Starting Jira to Database sync...")
    
    # Initialize clients
    jira = JiraClient()
    db = Database()
    
    try:
        # Connect to database
        if not db.connect():
            logger.error("Failed to connect to database")
            return
        
        # Initialize database tables
        if not db.init_tables():
            logger.error("Failed to initialize database tables")
            return
        
        # Get project data
        logger.info("Fetching project data...")
        project = jira.get_project()
        if not project:
            logger.error("Failed to fetch project data")
            return
        
        # Get issues data
        logger.info("Fetching issues data...")
        issues = jira.get_all_issues()
        if not issues:
            logger.error("Failed to fetch issues data")
            return
        
        # Save to database
        logger.info(f"Saving {len(issues)} issues to database...")
        if db.save_issues(project, issues):
            logger.info("Sync completed successfully!")
            
            # Show stats
            stats = db.get_stats()
            if stats:
                logger.info(f"Total Issues: {stats['total_issues']}")
                logger.info(f"Active: {stats['active_issues']}")
                logger.info(f"Closed: {stats['closed_issues']}")
                logger.info(f"Todo: {stats['todo_issues']}")
        else:
            logger.error("Failed to save to database")
    
    except Exception as e:
        logger.error(f"Sync failed: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_database()
    else:
        main()
