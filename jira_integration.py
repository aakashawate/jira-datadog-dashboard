#!/usr/bin/env python3
"""
Jira to Database Integration

Complete integration solution for syncing Jira issues to MySQL database.
Includes configuration, database operations, Jira API client, and main execution.

Author: Development Team
Version: 1.0
"""

import os
import json
import requests
import logging
from datetime import datetime
from pathlib import Path

# Optional MySQL import - only if database storage is needed
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("ℹ️  MySQL connector not available - using file system storage only")

# Import configuration from central config file
import config

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Application configuration settings - uses central config.py"""
    
    # Import Jira settings from config.py (single source of truth)
    JIRA_BASE_URL = config.JIRA_BASE_URL
    JIRA_EMAIL = config.JIRA_EMAIL
    JIRA_API_TOKEN = config.JIRA_API_TOKEN
    JIRA_PROJECT_ID = getattr(config, 'JIRA_PROJECT_ID', 'DP')
    JIRA_PROJECT_KEY = "DP"    # Project key for Donation Platform
    JIRA_MAX_RESULTS = getattr(config, 'JIRA_MAX_RESULTS', 100)
    
    # Storage Configuration
    USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true' and MYSQL_AVAILABLE
    
    # File System Configuration - Donation Platform specific
    DATA_DIR = os.getenv('DATA_DIR', 'donation_platform_data')
    PROJECTS_FILE = os.path.join(DATA_DIR, 'donation_project.json')
    ISSUES_FILE = os.path.join(DATA_DIR, 'donation_issues.json')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
    
    # Database Configuration - Donation Platform specific
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USERNAME = os.getenv('DB_USER', 'donation_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'donation_password')
    DB_DATABASE = os.getenv('DB_NAME', 'donation_platform')

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
                closed_date DATETIME NULL,
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
                        status, priority, issue_type, created_date, updated_date, closed_date,
                        assignee, reporter
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        summary = VALUES(summary),
                        description = VALUES(description),
                        status = VALUES(status),
                        priority = VALUES(priority),
                        issue_type = VALUES(issue_type),
                        updated_date = VALUES(updated_date),
                        closed_date = VALUES(closed_date),
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
                    issue.get('closed_date'),
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
# FILE SYSTEM STORAGE
# ============================================================================

class FileSystemStorage:
    """File system storage for Jira data"""
    
    def __init__(self):
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        Path(Config.DATA_DIR).mkdir(exist_ok=True)
        Path(Config.BACKUP_DIR).mkdir(exist_ok=True)
        logger.info("File system directories initialized")
    
    def create_backup(self):
        """Create backup of existing data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup projects
        if os.path.exists(Config.PROJECTS_FILE):
            backup_projects = os.path.join(Config.BACKUP_DIR, f"projects_{timestamp}.json")
            os.rename(Config.PROJECTS_FILE, backup_projects)
            logger.info(f"Projects backed up to {backup_projects}")
        
        # Backup issues
        if os.path.exists(Config.ISSUES_FILE):
            backup_issues = os.path.join(Config.BACKUP_DIR, f"issues_{timestamp}.json")
            os.rename(Config.ISSUES_FILE, backup_issues)
            logger.info(f"Issues backed up to {backup_issues}")
    
    def save_issues(self, project_data, issues_data):
        """Save project and issues to JSON files - ALWAYS FRESH DATA"""
        try:
            # Save project data with current timestamp
            project_with_timestamp = {
                **project_data,
                'last_updated': datetime.now().isoformat(),
                'issues_count': len(issues_data)
            }
            
            with open(Config.PROJECTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(project_with_timestamp, f, indent=2, ensure_ascii=False, default=str)
            
            # Save issues data with current timestamp - ALWAYS OVERWRITE
            issues_with_metadata = {
                'project_id': project_data['id'],
                'project_key': project_data['key'],
                'last_updated': datetime.now().isoformat(),
                'total_issues': len(issues_data),
                'issues': issues_data
            }
            
            with open(Config.ISSUES_FILE, 'w', encoding='utf-8') as f:
                json.dump(issues_with_metadata, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"FRESH DATA: Saved {len(issues_data)} issues with timestamp {datetime.now().isoformat()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to file system: {e}")
            return False
    
    def load_issues(self):
        """Load issues from file system"""
        try:
            if not os.path.exists(Config.ISSUES_FILE):
                return None
            
            with open(Config.ISSUES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load issues: {e}")
            return None
    
    def load_project(self):
        """Load project from file system"""
        try:
            if not os.path.exists(Config.PROJECTS_FILE):
                return None
            
            with open(Config.PROJECTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return None
    
    def get_stats(self):
        """Get project statistics from file system"""
        try:
            data = self.load_issues()
            if not data or 'issues' not in data:
                return None
            
            issues = data['issues']
            stats = {
                'total_issues': len(issues),
                'active_issues': sum(1 for issue in issues if issue.get('status', '').lower() in ['in progress', 'open', 'reopened']),
                'closed_issues': sum(1 for issue in issues if issue.get('status', '').lower() in ['closed', 'resolved', 'done']),
                'todo_issues': sum(1 for issue in issues if issue.get('status', '').lower() == 'to do'),
                'last_updated': data.get('last_updated', 'Unknown')
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get file system stats: {e}")
            return None
    
    def get_file_paths(self):
        """Get paths to data files"""
        return {
            'projects_file': Config.PROJECTS_FILE,
            'issues_file': Config.ISSUES_FILE,
            'data_dir': Config.DATA_DIR,
            'backup_dir': Config.BACKUP_DIR
        }

# ============================================================================
# STORAGE FACTORY
# ============================================================================

class StorageFactory:
    """Factory to create appropriate storage based on configuration"""
    
    @staticmethod
    def create_storage():
        """Create storage instance based on configuration"""
        if Config.USE_DATABASE:
            logger.info("Using Database storage")
            return Database()
        else:
            logger.info("Using File System storage")
            return FileSystemStorage()

# ============================================================================
# UNIVERSAL STORAGE INTERFACE
# ============================================================================

class StorageManager:
    """Universal storage manager that works with both DB and File System"""
    
    def __init__(self):
        self.storage = StorageFactory.create_storage()
        self.is_database = isinstance(self.storage, Database)
    
    def initialize(self):
        """Initialize storage (connect to DB or create directories)"""
        if self.is_database:
            success = self.storage.connect()
            if success:
                success = self.storage.init_tables()
            return success
        else:
            self.storage.ensure_directories()
            return True
    
    def save_data(self, project_data, issues_data):
        """Save data using appropriate storage method"""
        return self.storage.save_issues(project_data, issues_data)
    
    def get_statistics(self):
        """Get statistics from storage"""
        return self.storage.get_stats()
    
    def cleanup(self):
        """Cleanup storage connections"""
        if self.is_database:
            self.storage.close()
        # File system doesn't need cleanup
    
    def get_storage_info(self):
        """Get storage configuration info"""
        if self.is_database:
            return {
                'type': 'Database',
                'host': Config.DB_HOST,
                'database': Config.DB_DATABASE,
                'user': Config.DB_USERNAME
            }
        else:
            return {
                'type': 'File System',
                **self.storage.get_file_paths()
            }

# ============================================================================
# JIRA CLIENT
# ============================================================================

class JiraClient:
    """Jira API client for fetching project and issue data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.auth = (Config.JIRA_EMAIL, Config.JIRA_API_TOKEN)
        
    def get_project(self):
        """Get project details - try both ID and key"""
        # First try with project ID
        url = f"{Config.JIRA_BASE_URL}/rest/api/3/project/{Config.JIRA_PROJECT_ID}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.info(f"Failed to get project by ID {Config.JIRA_PROJECT_ID}: {e}")
            
            # Try with project key
            url = f"{Config.JIRA_BASE_URL}/rest/api/3/project/{Config.JIRA_PROJECT_KEY}"
            try:
                response = self.session.get(url)
                response.raise_for_status()
                return response.json()
            except Exception as e2:
                logger.error(f"Failed to get project by key {Config.JIRA_PROJECT_KEY}: {e2}")
                return None
    
    def get_all_issues(self):
        """Get all issues from the project"""
        issues = []
        start_at = 0
        
        while True:
            url = f"{Config.JIRA_BASE_URL}/rest/api/3/search"
            params = {
                'jql': f'project = "{Config.JIRA_PROJECT_KEY}"',
                'startAt': start_at,
                'maxResults': Config.JIRA_MAX_RESULTS,
                'fields': 'id,key,summary,description,status,priority,issuetype,created,updated,resolutiondate,assignee,reporter'
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
                        'closed_date': self._parse_date(issue['fields'].get('resolutiondate')),
                        'assignee': issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else '',
                        'reporter': issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else '',
                        # Additional fields for display
                        'created_by': issue['fields']['reporter']['displayName'] if issue['fields'].get('reporter') else '',
                        'assigned_to': issue['fields']['assignee']['displayName'] if issue['fields'].get('assignee') else 'Unassigned'
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
    """Setup database and user for Donation Platform Jira integration"""
    
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
        
        print("Creating Donation Platform database...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_DATABASE}")
        
        print("Creating Donation Platform database user...")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{Config.DB_USERNAME}'@'%' IDENTIFIED BY '{Config.DB_PASSWORD}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {Config.DB_DATABASE}.* TO '{Config.DB_USERNAME}'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        
        print("Donation Platform database setup completed successfully!")
        print(f"Database: {Config.DB_DATABASE}")
        print(f"User: {Config.DB_USERNAME}")
        print("Your Donation Platform Jira integration is ready!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Database setup failed: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('donation_platform_sync.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main synchronization function for Donation Platform project"""
    logger.info("Starting Donation Platform Jira sync...")
    
    # Initialize clients
    jira = JiraClient()
    storage = StorageManager()
    
    try:
        # Show storage configuration
        storage_info = storage.get_storage_info()
        logger.info(f"Storage Type: {storage_info['type']}")
        logger.info(f"Project: Donation Platform (DP) - ID: {Config.JIRA_PROJECT_ID}")
        
        if storage_info['type'] == 'File System':
            logger.info(f"Data Directory: {storage_info['data_dir']}")
        else:
            logger.info(f"Database: {storage_info['database']} at {storage_info['host']}")
        
        # Initialize storage
        if not storage.initialize():
            logger.error("Failed to initialize storage")
            return
        
        # Get project data
        logger.info("Fetching Donation Platform project data...")
        project = jira.get_project()
        if not project:
            logger.warning("Failed to fetch project data, using fallback project info")
            # Create fallback project data
            project = {
                'id': Config.JIRA_PROJECT_ID,
                'key': Config.JIRA_PROJECT_KEY,
                'name': 'Donation Platform',
                'projectTypeKey': 'software'
            }
        else:
            logger.info(f"Project: {project.get('name', 'Unknown')} ({project.get('key', 'Unknown')})")
        
        # Get issues data (this is the most important part)
        logger.info("Fetching Donation Platform issues...")
        issues = jira.get_all_issues()
        if not issues:
            logger.error("Failed to fetch Donation Platform issues")
            return
        
        # Save to storage
        logger.info(f"Saving {len(issues)} Donation Platform issues to {storage_info['type'].lower()}...")
        if storage.save_data(project, issues):
            logger.info("Donation Platform sync completed successfully!")
            
            # Show stats
            stats = storage.get_statistics()
            if stats:
                logger.info("=== DONATION PLATFORM STATISTICS ===")
                logger.info(f"Total Issues: {stats.get('total_issues', 0)}")
                logger.info(f"Active: {stats.get('active_issues', 0)}")
                logger.info(f"Closed: {stats.get('closed_issues', 0)}")
                logger.info(f"Todo: {stats.get('todo_issues', 0)}")
                if 'last_updated' in stats:
                    logger.info(f"Last Updated: {stats['last_updated']}")
        else:
            logger.error("Failed to save Donation Platform data to storage")
    
    except Exception as e:
        logger.error(f"Donation Platform sync failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        storage.cleanup()

if __name__ == "__main__":
    import sys
    
    def show_help():
        """Show help information"""
        print(f"""
Donation Platform Jira Integration Tool

Usage:
    python jira_integration.py                    # Sync Donation Platform data
    python jira_integration.py --setup            # Setup database (if using DB)
    python jira_integration.py --filesystem       # Force use file system
    python jira_integration.py --database         # Force use database
    python jira_integration.py --stats            # Show current statistics
    python jira_integration.py --help             # Show this help

Configuration:
    - Configured for Donation Platform project only
    - Set USE_DATABASE environment variable to 'true' for database mode
    - Default mode is file system storage in 'donation_platform_data/' directory

Current Configuration:
    - Jira URL: {Config.JIRA_BASE_URL}
    - Project: Donation Platform (DP)
    - Project ID: {Config.JIRA_PROJECT_ID}
    - Storage: {'Database' if Config.USE_DATABASE else 'File System'}
        """)
    
    def show_stats_only():
        """Show Donation Platform statistics without running sync"""
        storage = StorageManager()
        if not storage.initialize():
            print("Failed to initialize storage")
            return
        
        stats = storage.get_statistics()
        if stats:
            print("=== DONATION PLATFORM STATISTICS ===")
            print(f"Total Issues: {stats.get('total_issues', 0)}")
            print(f"Active: {stats.get('active_issues', 0)}")
            print(f"Closed: {stats.get('closed_issues', 0)}")
            print(f"Todo: {stats.get('todo_issues', 0)}")
            if 'last_updated' in stats:
                print(f"Last Updated: {stats['last_updated']}")
        else:
            print("No Donation Platform statistics available")
        
        storage.cleanup()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--setup":
            setup_database()
        elif arg == "--filesystem":
            Config.USE_DATABASE = False
            print("Forced file system mode for Donation Platform")
            main()
        elif arg == "--database":
            Config.USE_DATABASE = True
            print("Forced database mode for Donation Platform")
            main()
        elif arg == "--stats":
            show_stats_only()
        elif arg in ["--help", "-h", "help"]:
            show_help()
        else:
            print(f"Unknown argument: {arg}")
            show_help()
    else:
        main()
