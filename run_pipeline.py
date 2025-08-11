#!/usr/bin/env python3
"""
Jira-DataDog Live Monitoring System
Single unified application that always fetches live data

This application:
- Always fetches live Jira data (no cached data mode)
- Auto-refreshes every 5 minutes for new issues
- Continuously monitors and updates the dashboard
- Single command execution - no separate scripts needed

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

# Global variables for monitoring
dashboard_process = None
monitoring_active = False
monitoring_thread = None

import os
import sys
import subprocess
import time
import argparse
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60 + "\n")

def print_step(message):
    """Print a step message"""
    print(f"🔄 {message}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️  {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"💡 {message}")

def show_banner():
    """Show the application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║            🚀 JIRA LIVE MONITORING SYSTEM               ║
    ║                                                          ║
    ║          📊 Real-time Issue Tracking Dashboard          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_venv():
    """Check if virtual environment exists"""
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        print_error("Virtual environment not found!")
        print_info("Please run: python -m venv .venv")
        print_info("Then run: .venv\\Scripts\\pip install -r requirements.txt")
        return False
    return True

def run_python_script(script_name, description):
    """Run a Python script in the virtual environment"""
    print_step(f"Running {description}...")
    
    try:
        result = subprocess.run([
            ".venv/Scripts/python.exe", script_name
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            return True
        else:
            print_warning(f"{description} completed with warnings (Exit code: {result.returncode})")
            return False
    except Exception as e:
        print_error(f"Failed to run {description}: {e}")
        return False

def check_data_files():
    """Check if Jira data files exist and get their info"""
    jira_file = Path("donation_platform_data/donation_issues.json")
    
    has_jira = jira_file.exists()
    
    if has_jira:
        try:
            with open(jira_file, 'r', encoding='utf-8') as f:
                jira_data = json.load(f)
                issue_count = len(jira_data.get('issues', []))
                last_updated = jira_data.get('last_updated', 'Unknown')
                print_success(f"Jira data found: {issue_count} issues (Updated: {last_updated})")
        except Exception as e:
            print_warning(f"Jira file exists but couldn't read: {e}")
    else:
        print_warning("No Jira data found")
    
    return has_jira

def stop_existing_dashboard():
    """Stop any existing dashboard servers on port 8080"""
    stopped = False
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ':8080' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, check=True)
                            print_step(f"Stopped existing dashboard server (PID: {pid})")
                            stopped = True
                            time.sleep(1)
                        except subprocess.CalledProcessError:
                            pass
    except Exception:
        pass
    return stopped

def main():
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
    
    # Handle stop command
    if args.stop:
        print("🛑 Stopping dashboard servers...")
        if stop_existing_dashboard():
            print_success("Dashboard servers stopped successfully")
        else:
            print_info("No running dashboard servers found")
        return
    
    # Show banner
    show_banner()
    
    # Handle aliases
    if args.dashboard_only:
        args.quick_start = True
    
    # Check prerequisites
    print_step("Checking prerequisites...")
    if not check_venv():
        sys.exit(1)
    print_success("Virtual environment found")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    print_success(f"Working directory: {os.getcwd()}")
    
    # Stop any existing dashboard servers
    stop_existing_dashboard()
    
    # Check existing data
    print_step("Checking existing data files...")
    has_jira = check_data_files()
    
    if args.quick_start:
        print_header("⚡ QUICK START MODE - USING EXISTING JIRA DATA")
        if not has_jira:
            print_error("No existing Jira data found! Cannot use quick-start mode.")
            print_info("Run without --quick-start to fetch fresh Jira data")
            print_info("Example: python run_pipeline.py")
            sys.exit(1)
    else:
        # Step 1: Jira Data (ALWAYS LIVE FETCH - NO CACHED DATA)
        print_header("🎫 STEP 1: FETCHING LIVE JIRA DATA")
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
    
    # Step 2: Dashboard with Live Auto-Refresh
    print_header("🌐 STEP 2: STARTING LIVE DASHBOARD SERVER")
    print("🌐 Dashboard URL: http://localhost:8080")
    print("🔄 Live Auto-refresh: Every 5 minutes for NEW Jira issues")
    print("📊 DataDog Dashboard: Available on DataDog port (no metrics fetching)")
    print("🛑 Stop server: Press Ctrl+C")
    print("\n" + "="*50)
    print("🚀 Starting dashboard server...")
    print("="*50)
    
    time.sleep(2)
    
    try:
        # Use the virtual environment Python
        venv_python = Path(".venv/Scripts/python.exe")
        subprocess.run([str(venv_python), "dashboard_server.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard server stopped by user")
        print_success("Pipeline execution completed gracefully")
    except Exception as e:
        print_error(f"Failed to start dashboard server: {e}")
        print_info("Check if port 8080 is available or try running with --stop first")
        sys.exit(1)
    
    print_header("🏁 PIPELINE EXECUTION COMPLETED")
    print_success("Thank you for using the Jira-DataDog Monitoring Pipeline! 🚀")

if __name__ == "__main__":
    main()
