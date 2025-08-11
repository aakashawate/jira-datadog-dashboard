#!/usr/bin/env python3
"""
Live Dashboard Server for Jira Monitoring System
Serves the HTML dashboard with live auto-refresh of Jira data every 5 minutes
"""

import http.server
import socketserver
import json
import os
import webbrowser
import subprocess
import sys
from urllib.parse import urlparse
import threading
import time
from datetime import datetime
from pathlib import Path

# Global variable to track the auto-refresh thread
refresh_thread = None
stop_refresh = False

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Parse the request path
        parsed_path = urlparse(self.path)
        
        # Default to serving the dashboard
        if self.path == '/' or self.path == '':
            self.path = '/unified_dashboard.html'
        
        # Handle JSON data requests with proper content type
        if self.path.endswith('.json'):
            try:
                # Serve JSON files with correct content type
                with open(self.path[1:], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
                return
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
                return
        
        # Default handling for other files
        super().do_GET()

def run_jira_fetch():
    """Run Jira integration to fetch fresh data"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-refreshing Jira data...")
        
        # Get the Python executable from virtual environment
        venv_python = Path(".venv/Scripts/python.exe")
        if venv_python.exists():
            result = subprocess.run([str(venv_python), "jira_integration.py"], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run([sys.executable, "jira_integration.py"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"SUCCESS: [{datetime.now().strftime('%H:%M:%S')}] Jira data refreshed successfully")
        else:
            print(f"WARNING: [{datetime.now().strftime('%H:%M:%S')}] Jira refresh completed with warnings")
            
    except Exception as e:
        print(f"ERROR: [{datetime.now().strftime('%H:%M:%S')}] Error refreshing Jira data: {e}")

def auto_refresh_jira():
    """Auto-refresh Jira data every 5 minutes"""
    global stop_refresh
    
    while not stop_refresh:
        # Wait for 5 minutes (300 seconds)
        for _ in range(300):  # Check every second for stop signal
            if stop_refresh:
                return
            time.sleep(1)
        
        if not stop_refresh:
            run_jira_fetch()

def start_dashboard_server(port=8080):
    """Start the dashboard server with live auto-refresh"""
    global refresh_thread, stop_refresh
    
    print(f"🚀 Starting Live Jira Monitoring Dashboard Server...")
    print(f"📁 Serving from: {os.getcwd()}")
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        dashboard_url = f"http://localhost:{port}"
        print(f"🌐 Dashboard available at: {dashboard_url}")
        print(f"📊 Jira data loaded from: donation_platform_data/donation_issues.json")
        print(f"🔄 Live auto-refresh: Fetching new Jira issues every 5 minutes")
        print(f"💡 Press Ctrl+C to stop the server")
        
        # Start auto-refresh thread
        stop_refresh = False
        refresh_thread = threading.Thread(target=auto_refresh_jira, daemon=True)
        refresh_thread.start()
        print(f"✅ Auto-refresh thread started")
        
        # Auto-open browser after a short delay
        def open_browser():
            time.sleep(2)
            print(f"🔗 Opening dashboard in browser...")
            webbrowser.open(dashboard_url)
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Shutting down dashboard server...")
            stop_refresh = True
            httpd.shutdown()

def check_data_files():
    """Check if required data files exist"""
    issues_file = "donation_platform_data/donation_issues.json"
    project_file = "donation_platform_data/donation_project.json"
    
    print("🔍 Checking data files...")
    
    if not os.path.exists(issues_file):
        print(f"❌ Jira issues data not found: {issues_file}")
        print(f"💡 Run 'python jira_integration.py' first to fetch Jira data")
        return False
    
    if not os.path.exists(project_file):
        print(f"⚠️  Project data not found: {project_file}")
        print(f"💡 Run 'python jira_integration.py' first to fetch project data")
    
    # Check if data is recent
    try:
        with open(issues_file, 'r') as f:
            data = json.load(f)
        
        last_updated = data.get('last_updated', 'Unknown')
        total_issues = data.get('total_issues', 0)
        
        print(f"✅ Found Jira data:")
        print(f"   📊 Total Issues: {total_issues}")
        print(f"   🕐 Last Updated: {last_updated}")
        print(f"   📁 File: {issues_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Jira data: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 JIRA LIVE MONITORING DASHBOARD")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("unified_dashboard.html"):
        print("❌ Dashboard file not found in current directory")
        print("💡 Make sure you're in the jira-issues-fetch directory")
        return
    
    # Check data files
    if not check_data_files():
        print("\n🔄 Attempting to fetch fresh Jira data...")
        try:
            # Use virtual environment Python if available
            venv_python = Path(".venv/Scripts/python.exe")
            if venv_python.exists():
                subprocess.run([str(venv_python), "jira_integration.py"], check=True)
            else:
                subprocess.run([sys.executable, "jira_integration.py"], check=True)
            print("✅ Jira data updated")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to update Jira data: {e}")
            print("💡 Please run 'python jira_integration.py' manually")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Start the server with live refresh
    try:
        start_dashboard_server(8080)
    except OSError as e:
        if "Address already in use" in str(e):
            print("❌ Port 8080 is already in use")
            print("💡 Try a different port or stop the existing server")
            try:
                start_dashboard_server(8081)
            except:
                print("❌ Port 8081 also in use. Please stop other servers.")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
