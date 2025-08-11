#!/usr/bin/env python3
"""
Simple Dashboard Server for Unified Monitoring Dashboard
Serves the HTML dashboard and Jira data with proper CORS headers
"""

import http.server
import socketserver
import json
import os
import webbrowser
from urllib.parse import urlparse
import threading
import time

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

def start_dashboard_server(port=8080):
    """Start the dashboard server"""
    print(f"🚀 Starting Unified Monitoring Dashboard Server...")
    print(f"📁 Serving from: {os.getcwd()}")
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        dashboard_url = f"http://localhost:{port}"
        print(f"🌐 Dashboard available at: {dashboard_url}")
        print(f"📊 Jira data will be loaded from: donation_platform_data/donation_issues.json")
        print(f"🔄 Dashboard will auto-refresh Jira data every 5 minutes")
        print(f"\n💡 Press Ctrl+C to stop the server")
        
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
    print("🎯 UNIFIED MONITORING DASHBOARD")
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
            os.system("python jira_integration.py")
            print("✅ Jira data updated")
        except Exception as e:
            print(f"❌ Failed to update Jira data: {e}")
            print("💡 Please run 'python jira_integration.py' manually")
    
    print("\n" + "=" * 60)
    
    # Start the server
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
