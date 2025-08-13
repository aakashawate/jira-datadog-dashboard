#!/usr/bin/env python3
"""
Jira-DataDog Live Monitoring System with Comprehensive Logging
Single unified application that always fetches live data

This application:
- Always fetches live Jira data (no cached data mode)
- Auto-refreshes every 5 minutes for real-time updates
- Continuously monitors and updates the dashboard
- Single command execution - no separate scripts needed
- Comprehensive logging for production deployment

Usage:
    python run_pipeline.py                    # Start live monitoring system
    python run_pipeline.py --stop             # Stop running servers
"""

import os
import sys
import subprocess
import time
import argparse
import json
import threading
import signal
import atexit
from pathlib import Path
from datetime import datetime

# Import shared utilities
from utils import MessageUtils, SystemUtils, FileUtils, ConfigManager, Logger

# Initialize logger for this module
logger = Logger.get_logger('pipeline')

# Global variables for monitoring
dashboard_process = None
monitoring_active = False
monitoring_thread = None

def print_header(title):
    """Print a formatted header"""
    MessageUtils.print_header(title)

def print_step(message):
    """Print a step message"""
    MessageUtils.print_step(message)

def print_success(message):
    """Print a success message"""
    MessageUtils.print_success(message)

def print_warning(message):
    """Print a warning message"""
    MessageUtils.print_warning(message)

def print_error(message):
    """Print an error message"""
    MessageUtils.print_error(message)

def print_info(message):
    """Print an info message"""
    MessageUtils.print_info(message)

def show_banner():
    """Show the application banner with logging"""
    logger.info("Displaying application banner")
    banner = """
    ==============================================================
                                                               
                JIRA LIVE MONITORING SYSTEM                   
                                                               
             Real-time Issue Tracking Dashboard               
                                                               
    ==============================================================
    """
    print(banner)

def check_venv():
    """Check if virtual environment exists with logging"""
    logger.info("Checking virtual environment setup")
    if not SystemUtils.check_virtual_environment():
        logger.warning("Virtual environment not found")
        print_error("Virtual environment not found!")
        print_info("Please run: python -m venv .venv")
        print_info("Then run: .venv\\Scripts\\pip install -r requirements.txt")
        return False
    return True

def run_python_script(script_name, description):
    """Run a Python script in the virtual environment with logging"""
    logger.info(f"Running script: {script_name} ({description})")
    print_step(f"Running {description}...")
    
    try:
        result = SystemUtils.run_script_in_venv(script_name, capture_output=False)
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            logger.info(f"Script {script_name} completed successfully")
            return True
        else:
            print_warning(f"{description} completed with warnings (Exit code: {result.returncode})")
            logger.warning(f"Script {script_name} completed with exit code: {result.returncode}")
            return False
    except Exception as e:
        print_error(f"Failed to run {description}: {e}")
        logger.error(f"Failed to run script {script_name}: {str(e)}", exc_info=True)
        return False

def check_data_files():
    """Check if Jira data files exist and get their info with logging"""
    logger.info("Checking existing data files")
    jira_file = Path("donation_platform_data/donation_issues.json")
    
    has_jira = jira_file.exists()
    
    if has_jira:
        try:
            jira_data = FileUtils.read_json_file(jira_file)
            issue_count = len(jira_data.get('issues', []))
            last_updated = jira_data.get('last_updated', 'Unknown')
            print_success(f"Jira data found: {issue_count} issues (Updated: {last_updated})")
            logger.info(f"Found Jira data: {issue_count} issues, last updated: {last_updated}")
        except Exception as e:
            print_warning(f"Jira file exists but couldn't read: {e}")
            logger.warning(f"Could not read Jira data file: {str(e)}")
    else:
        print_warning("No Jira data found")
    
    return has_jira

def stop_existing_dashboard():
    """Stop any existing dashboard servers on port 8080"""
    stopped = SystemUtils.stop_process_on_port(8080)
    if stopped:
        print_step("Stopped existing dashboard server")
        time.sleep(1)
    return stopped

def main():
    """Main application entry point with comprehensive logging"""
    logger.info("=== STARTING MAIN APPLICATION ===")
    
    parser = argparse.ArgumentParser(
        description="Jira Live Monitoring System - Real-time Issue Tracking Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                    # Live Jira monitoring (recommended)
  python run_pipeline.py --quick-start      # Dashboard only with existing data
  python run_pipeline.py --stop             # Stop running servers only

Dashboard will be available at: http://localhost:8080
Auto-refreshes Jira data every 5 minutes for new issues
        """
    )
    parser.add_argument("--quick-start", action="store_true", 
                       help="Use existing data, start dashboard immediately")
    parser.add_argument("--dashboard-only", action="store_true", 
                       help="Start dashboard only (alias for --quick-start)")
    parser.add_argument("--stop", action="store_true", 
                       help="Stop any running dashboard servers and exit")
    
    args = parser.parse_args()
    logger.info(f"Command line arguments: {args}")
    
    # Handle stop command
    if args.stop:
        logger.info("Stop command requested")
        print("Stopping dashboard servers...")
        if stop_existing_dashboard():
            print_success("Dashboard servers stopped successfully")
            logger.info("Dashboard servers stopped successfully")
        else:
            print_info("No running dashboard servers found")
            logger.info("No running dashboard servers found")
        return
    
    # Show banner
    show_banner()
    
    # Handle aliases
    if args.dashboard_only:
        args.quick_start = True
        logger.info("Dashboard-only mode enabled")
    
    # Check prerequisites
    logger.info("Starting prerequisite checks")
    print_step("Checking prerequisites...")
    if not check_venv():
        logger.error("Virtual environment check failed")
        sys.exit(1)
    print_success("Virtual environment found")
    logger.info("Virtual environment check passed")
    
    # Show current working directory
    cwd = os.getcwd()
    print_success(f"Working directory: {cwd}")
    logger.info(f"Working directory: {cwd}")
    
    # Stop any existing dashboard servers
    logger.info("Stopping any existing dashboard servers")
    if stop_existing_dashboard():
        logger.info("Existing dashboard server stopped")
        time.sleep(2)
    
    # Check existing data
    logger.info("Checking existing data files")
    print_step("Checking existing data files...")
    check_data_files()
    
    # Step 1: Data fetch (unless quick-start)
    if not args.quick_start:
        # Step 1: Jira Data (ALWAYS LIVE FETCH - NO CACHED DATA)
        print_header("STEP 1: FETCHING LIVE JIRA DATA")
        print_info("Always fetching fresh data from Jira API (no cached data)")
        success = run_python_script("jira_integration.py", "Live Jira data fetch")
        if success:
            print_success("Live Jira data fetched successfully")
        else:
            print_warning("Jira integration completed with warnings, continuing...")
            # Don't exit, continue with existing data
    
    # Final data validation
    print_step("Final data validation...")
    has_jira = check_data_files()
    
    if not has_jira:
        print_error("No Jira data available for dashboard!")
        print_info("Failed to fetch fresh Jira data from API")
        sys.exit(1)
    
    # Step 2: Live Dashboard with Fast Auto-Refresh
    logger.info("Starting dashboard server")
    print_header("STEP 2: STARTING LIVE DASHBOARD SERVER")
    print("Dashboard URL: http://localhost:8080")
    print("Live Auto-refresh: Every 5 minutes for NEW Jira issues")
    print("DataDog Dashboard: Available on DataDog port (no metrics fetching)")
    print("Stop server: Press Ctrl+C")
    print("\n" + "="*50)
    print("Starting dashboard server...")
    print("="*50)
    
    time.sleep(2)
    
    try:
        # Use the virtual environment Python
        venv_python = Path(".venv/Scripts/python.exe")
        logger.info(f"Starting dashboard server with Python: {venv_python}")
        subprocess.run([str(venv_python), "dashboard_server.py"])
    except KeyboardInterrupt:
        logger.info("Dashboard server stopped by user (KeyboardInterrupt)")
        print("\n\nDashboard server stopped by user")
        print_success("Pipeline execution completed gracefully")
    except Exception as e:
        logger.error(f"Error running dashboard server: {str(e)}", exc_info=True)
        print_error(f"Failed to start dashboard server: {e}")
        print_info("Check if port 8080 is available or try running with --stop first")
        sys.exit(1)
    
    print_header("PIPELINE EXECUTION COMPLETED")
    print_success("Thank you for using the Jira-DataDog Monitoring Pipeline!")
    logger.info("=== PIPELINE EXECUTION COMPLETED ===")

if __name__ == "__main__":
    logger.info("Starting run_pipeline.py as main module")
    main()
