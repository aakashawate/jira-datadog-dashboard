#!/usr/bin/env python3
"""
Shared Utilities for Jira Monitoring System
Common functions and utilities used across multiple modules
"""

import os
import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import traceback

class Logger:
    """Centralized logging utility with production-ready configuration"""
    
    _loggers = {}
    
    @classmethod
    def setup_logger(cls, name, log_file=None, level=logging.INFO, max_bytes=10*1024*1024, backup_count=5):
        """Setup logger with rotating file handler and console output"""
        
        # Return existing logger if already configured
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Clear any existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation (for production)
        if log_file:
            # Ensure log directory exists
            log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, 
                maxBytes=max_bytes, 
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Store logger reference
        cls._loggers[name] = logger
        
        return logger
    
    @classmethod
    def get_logger(cls, name):
        """Get existing logger or create default one"""
        if name in cls._loggers:
            return cls._loggers[name]
        else:
            return cls.setup_logger(name, f'logs/{name}.log')
    
    @classmethod
    def log_exception(cls, logger, message="An error occurred"):
        """Log exception with full traceback"""
        logger.error(f"{message}: {str(sys.exc_info()[1])}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    @classmethod
    def setup_application_logging(cls):
        """Setup logging for the entire application"""
        # Main application logger
        main_logger = cls.setup_logger('jira_monitoring', 'logs/jira_monitoring.log')
        
        # Component-specific loggers
        cls.setup_logger('jira_integration', 'logs/jira_integration.log')
        cls.setup_logger('dashboard_server', 'logs/dashboard_server.log')
        cls.setup_logger('pipeline', 'logs/pipeline.log')
        cls.setup_logger('system_utils', 'logs/system_utils.log')
        
        # System logger for critical issues
        cls.setup_logger('system_critical', 'logs/system_critical.log', level=logging.ERROR)
        
        main_logger.info("Application logging initialized")
        main_logger.info(f"Log files location: {os.path.abspath('logs')}")
        
        return main_logger

class FileUtils:
    """File operations utility"""
    
    @staticmethod
    def ensure_directory(directory_path):
        """Create directory if it doesn't exist"""
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_json_file(file_path, default=None):
        """Safely read JSON file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if default is not None:
                return default
            raise e
    
    @staticmethod
    def write_json_file(file_path, data, backup=True):
        """Write JSON file with optional backup"""
        if backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup"
            os.rename(file_path, backup_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_file_timestamp(file_path):
        """Get file modification timestamp"""
        if os.path.exists(file_path):
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        return None

class SystemUtils:
    """System operations utility with logging"""
    
    @staticmethod
    def check_virtual_environment():
        """Check if virtual environment exists and is active"""
        logger = Logger.get_logger('system_utils')
        venv_python = Path(".venv/Scripts/python.exe")
        
        if os.name != 'nt':  # Linux/Mac
            venv_python = Path(".venv/bin/python")
        
        exists = venv_python.exists()
        logger.info(f"Virtual environment check: {'Found' if exists else 'Not found'} at {venv_python}")
        return exists
    
    @staticmethod
    def run_script_in_venv(script_name, capture_output=False):
        """Run Python script in virtual environment with logging"""
        logger = Logger.get_logger('system_utils')
        
        # Determine Python executable path based on OS
        if os.name == 'nt':  # Windows
            python_cmd = Path(".venv/Scripts/python.exe")
        else:  # Linux/Mac
            python_cmd = Path(".venv/bin/python")
        
        if not python_cmd.exists():
            logger.warning(f"Virtual environment Python not found at {python_cmd}, using system Python")
            python_cmd = sys.executable
        
        logger.info(f"Running script: {script_name} with Python: {python_cmd}")
        
        try:
            result = subprocess.run(
                [str(python_cmd), script_name],
                capture_output=capture_output,
                text=True,
                timeout=300  # 5-minute timeout
            )
            
            logger.info(f"Script {script_name} completed with return code: {result.returncode}")
            
            if capture_output:
                if result.stdout:
                    logger.debug(f"Script stdout: {result.stdout[:500]}...")
                if result.stderr:
                    logger.warning(f"Script stderr: {result.stderr[:500]}...")
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Script {script_name} timed out after 5 minutes")
            raise
        except Exception as e:
            logger.error(f"Failed to run script {script_name}: {str(e)}")
            raise
    
    @staticmethod
    def stop_process_on_port(port):
        """Stop process running on specific port with logging"""
        logger = Logger.get_logger('system_utils')
        logger.info(f"Attempting to stop process on port {port}")
        
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=30)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, check=True, timeout=10)
                                logger.info(f"Successfully stopped process PID {pid} on port {port}")
                                return True
                            except subprocess.CalledProcessError as e:
                                logger.warning(f"Failed to kill process PID {pid}: {e}")
            else:  # Linux/Mac
                result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True, timeout=30)
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(['kill', '-9', pid], capture_output=True, check=True, timeout=10)
                            logger.info(f"Successfully stopped process PID {pid} on port {port}")
                            return True
                        except subprocess.CalledProcessError as e:
                            logger.warning(f"Failed to kill process PID {pid}: {e}")
                            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while trying to stop process on port {port}")
        except Exception as e:
            logger.error(f"Error stopping process on port {port}: {str(e)}")
        
        logger.info(f"No process found or stopped on port {port}")
        return False
    
    @staticmethod
    def get_system_info():
        """Get system information for logging"""
        logger = Logger.get_logger('system_utils')
        
        info = {
            'os': os.name,
            'platform': sys.platform,
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"System info: {info}")
        return info

class MessageUtils:
    """Consistent messaging utility"""
    
    @staticmethod
    def print_header(title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60 + "\n")
    
    @staticmethod
    def print_step(message):
        """Print step message"""
        print(f"Step: {message}")
    
    @staticmethod
    def print_success(message):
        """Print success message"""
        print(f"SUCCESS: {message}")
    
    @staticmethod
    def print_warning(message):
        """Print warning message"""
        print(f"WARNING: {message}")
    
    @staticmethod
    def print_error(message):
        """Print error message"""
        print(f"ERROR: {message}")
    
    @staticmethod
    def print_info(message):
        """Print info message"""
        print(f"INFO: {message}")

class DataValidator:
    """Data validation utility"""
    
    @staticmethod
    def validate_jira_config(config):
        """Validate Jira configuration"""
        required_fields = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'JIRA_API_TOKEN']
        for field in required_fields:
            if not hasattr(config, field) or not getattr(config, field):
                raise ValueError(f"Missing required configuration: {field}")
        return True
    
    @staticmethod
    def validate_jira_response(response_data):
        """Validate Jira API response"""
        if not isinstance(response_data, dict):
            raise ValueError("Invalid response format")
        
        if 'issues' in response_data:
            return True
        elif 'id' in response_data and 'key' in response_data:
            return True
        else:
            raise ValueError("Unexpected response structure")
    
    @staticmethod
    def sanitize_issue_data(issue):
        """Sanitize and validate issue data"""
        required_fields = ['id', 'key', 'fields']
        for field in required_fields:
            if field not in issue:
                raise ValueError(f"Missing required issue field: {field}")
        
        return {
            'id': str(issue['id']),
            'key': str(issue['key']),
            'summary': issue['fields'].get('summary', 'No Summary'),
            'status': issue['fields'].get('status', {}).get('name', 'Unknown'),
            'created': issue['fields'].get('created', ''),
            'updated': issue['fields'].get('updated', ''),
            'assignee': issue['fields'].get('assignee', {}).get('displayName', 'Unassigned') if issue['fields'].get('assignee') else 'Unassigned',
            'priority': issue['fields'].get('priority', {}).get('name', 'None') if issue['fields'].get('priority') else 'None'
        }

class ConfigManager:
    """Configuration management utility"""
    
    @staticmethod
    def load_config():
        """Load configuration from config.py"""
        try:
            import config
            return config
        except ImportError:
            raise ImportError("Configuration file (config.py) not found")
    
    @staticmethod
    def get_data_directory(config):
        """Get data directory from config"""
        data_dir = getattr(config, 'DATA_DIR', 'donation_platform_data')
        FileUtils.ensure_directory(data_dir)
        return data_dir
    
    @staticmethod
    def get_refresh_interval(config):
        """Get refresh interval from config"""
        return getattr(config, 'REFRESH_INTERVAL', 300)  # Default 5 minutes
