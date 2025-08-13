# Jira-DataDog Live Monitoring Dashboard

A professional live monitoring system that integrates Jira issues with DataDog dashboard visualization. This system provides real-time tracking of Jira issues with automatic data refresh, clean web interface, and comprehensive production-ready logging.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture & Design](#architecture--design)
- [Code Structure](#code-structure)
- [Setup & Installation](#setup--installation)
- [Code Execution](#code-execution)
- [Configuration](#configuration)
- [Features](#features)
- [Logging System](#logging-system)
- [Data Flow](#data-flow)
- [API Integration](#api-integration)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## 🏗️ System Overview

### Purpose
Live monitoring dashboard for Jira issues with integrated DataDog metrics visualization. The system fetches fresh Jira data every 5 minutes and displays it in a responsive web interface with comprehensive logging for production deployment.

### Key Components
- **Jira Integration**: Fetches live issue data from Jira API
- **Data Storage**: File-based storage with optional MySQL support  
- **Live Dashboard**: Web server with auto-refresh capabilities
- **Configuration Management**: Centralized configuration system
- **Logging System**: Production-ready logging with rotation and monitoring
- **Shared Utilities**: Code reusability and consistent operations

## 🏛️ Architecture & Design

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Jira API      │◄───│  Integration    │────►│  Data Storage   │
│   (External)    │    │     Layer       │    │  (JSON Files)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄───│  Dashboard      │◄───│  Auto-Refresh   │
│   (localhost)   │    │     Server      │    │    System       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Logging System  │
                       │ (Production)    │
                       └─────────────────┘
```

### Design Principles
- **Single Responsibility**: Each module handles one specific concern
- **Configuration Centralization**: All settings in `config.py`
- **Error Handling**: Graceful failure handling with logging
- **Code Reusability**: Modular design for easy maintenance
- **Professional Standards**: Clean code without symbols or clutter

## 📁 Code Structure

### Core Files
```
├── run_pipeline.py           # Main entry point and orchestrator
├── config.py                 # Centralized configuration management
├── jira_integration.py       # Jira API client and data processing
├── dashboard_server.py       # Web server with auto-refresh
├── unified_dashboard.html    # Frontend dashboard interface
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation
```

### Data Files
```
├── donation_platform_data/
│   ├── donation_issues.json      # Current Jira issues data
│   ├── donation_project.json     # Project metadata
│   └── backups/                   # Automatic backups
└── .venv/                         # Python virtual environment
```

### Module Responsibilities

#### `config.py` - Configuration Management
- **Purpose**: Single source of truth for all system settings
- **Reusability**: Imported by all other modules
- **Contains**: Jira credentials, database settings, file paths, API limits

#### `jira_integration.py` - Data Integration Layer  
- **Purpose**: Handles all Jira API communication and data processing
- **Reusability**: Can be used standalone or integrated
- **Features**: OAuth authentication, data transformation, storage abstraction

#### `dashboard_server.py` - Presentation Layer
- **Purpose**: Web server with live data serving and auto-refresh
- **Reusability**: Independent web server that can serve any JSON data
- **Features**: Auto-refresh threading, CORS support, error handling

#### `run_pipeline.py` - Orchestration Layer
- **Purpose**: Main entry point that coordinates all components
- **Reusability**: Template for similar monitoring systems
- **Features**: Command-line interface, process management, graceful shutdown

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for Jira API access
- Web browser for dashboard viewing

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd jira-issues-fetch
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   source .venv/bin/activate   # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure System**
   ```bash
   # Edit config.py with your Jira credentials
   notepad config.py  # Windows
   # or
   nano config.py     # Linux/Mac
   ```

5. **Test Configuration**
   ```bash
   python jira_integration.py  # Test Jira connection
   ```

## 🚀 Code Execution

### Quick Start
```bash
# Start the complete monitoring system
python run_pipeline.py
```

### Advanced Usage
```bash
# Start with existing data (skip fresh fetch)
python run_pipeline.py --quick-start

# Dashboard only mode
python run_pipeline.py --dashboard-only

# Stop running servers
python run_pipeline.py --stop
```

### Execution Flow

1. **System Initialization**
   - Virtual environment validation
   - Dependency checking
   - Configuration loading

2. **Data Fetch Phase**
   - Jira API authentication
   - Project metadata retrieval
   - Issues data collection
   - Data validation and storage

3. **Dashboard Launch**
   - Web server startup on port 8080
   - Auto-refresh thread initialization
   - Browser launch
   - Continuous monitoring

4. **Runtime Operations**
   - Automatic data refresh every 5 minutes
   - Real-time dashboard updates
   - Error logging and recovery
   - Graceful shutdown handling

## ⚙️ Configuration

### Primary Configuration (`config.py`)

```python
# Jira Settings
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com" 
JIRA_API_TOKEN = "your-api-token"
JIRA_PROJECT_ID = "10000"

# System Settings
JIRA_MAX_RESULTS = 100
REFRESH_INTERVAL = 300  # 5 minutes
USE_DATABASE = False    # True for MySQL, False for files
```

### Environment Variables (Optional)
```bash
export USE_DATABASE=false
export DATA_DIR=donation_platform_data
export DB_HOST=localhost
export DB_PORT=3306
```

### Jira API Token Setup
1. Go to Jira → Account Settings → Security
2. Create API Token
3. Copy token to `config.py`

## ✨ Features

### Core Features
- **Live Data Fetching**: Fresh Jira data every 5 minutes
- **Web Dashboard**: Responsive HTML interface at `localhost:8080`
- **Auto-Refresh**: Background data updates without manual intervention
- **DataDog Integration**: Embedded DataDog dashboard iframe
- **Error Recovery**: Graceful handling of API failures

### Dashboard Features
- **Issue Statistics**: Count by status (To Do, In Progress, In Review, Done)
- **Real-time Updates**: Automatic data refresh with cache-busting
- **Responsive Design**: Works on desktop and mobile browsers
- **Status Visualization**: Color-coded issue status indicators

### Technical Features
- **Modular Design**: Reusable components
- **Configuration Management**: Centralized settings
- **Logging System**: Comprehensive error and info logging
- **Backup System**: Automatic data backups
- **Cross-Platform**: Works on Windows, Linux, Mac

## 📊 Logging System

### Overview
The system includes comprehensive production-ready logging designed for Linux server deployment. The logging system provides detailed tracking, debugging capabilities, and error monitoring across all components.

### Log Files Structure
```
logs/
├── jira_integration.log    # Jira API interactions, data fetching
├── dashboard_server.log    # Web server operations, HTTP requests
├── pipeline.log           # Main orchestration, monitoring cycles
├── system_utils.log       # System operations, environment checks
└── system_critical.log    # Critical system events, failures
```

### Key Features
- **Automatic Rotation**: Log files rotate at 10MB with 5 backups
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR with filtering
- **Detailed Format**: Timestamp, module, level, filename, line number
- **Exception Tracking**: Full stack traces for debugging
- **Production Ready**: Designed for Linux server monitoring

### Usage Examples
```bash
# Monitor all logs in real-time
tail -f logs/*.log

# Monitor specific component
tail -f logs/jira_integration.log

# Search for errors
grep -r "ERROR" logs/

# Monitor during operation
python run_pipeline.py
```

For detailed logging documentation, see [LOGGING_GUIDE.md](LOGGING_GUIDE.md)

## 📊 Data Flow

### High-Level Data Flow
```
Jira API → Authentication → Project Fetch → Issues Fetch → 
Data Transform → JSON Storage → Dashboard Display → Auto-Refresh Loop
```

### Detailed Process

1. **Authentication Flow**
   ```
   config.py → jira_integration.py → Jira OAuth → API Access
   ```

2. **Data Collection Flow**
   ```
   API Request → JSON Response → Data Validation → 
   Transform → Storage → Backup Creation
   ```

3. **Dashboard Flow**
   ```
   JSON Files → HTTP Server → Browser Request → 
   Data Serve → JavaScript Render → Auto-Refresh
   ```

4. **Refresh Flow**
   ```
   Background Thread → Timer (5 min) → Jira Fetch → 
   Data Update → Dashboard Refresh → Loop Continue
   ```

## 🔗 API Integration

### Jira REST API Usage

#### Authentication
```python
headers = {
    'Authorization': f'Basic {base64_credentials}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
```

#### Project Endpoint
```
GET /rest/api/3/project/{projectId}
```

#### Issues Endpoint  
```
GET /rest/api/3/search?jql=project={projectId}&maxResults={limit}
```

### Data Transformation
- **Issue Mapping**: Jira fields → Dashboard format
- **Status Normalization**: Jira status → Standard categories
- **Timestamp Handling**: UTC conversion and formatting
- **Error Sanitization**: Safe data handling

## � Production Deployment

### Linux Server Setup

#### 1. Environment Preparation
```bash
# Clone repository
git clone <repository-url>
cd jira-issues-fetch

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configuration
```bash
# Configure Jira credentials
nano config.py

# Test connection
python jira_integration.py
```

#### 3. Service Setup (systemd)
Create `/etc/systemd/system/jira-monitor.service`:
```ini
[Unit]
Description=Jira Live Monitoring System
After=network.target

[Service]
Type=simple
User=jira-monitor
WorkingDirectory=/opt/jira-monitor
Environment=PATH=/opt/jira-monitor/.venv/bin
ExecStart=/opt/jira-monitor/.venv/bin/python run_pipeline.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable jira-monitor
sudo systemctl start jira-monitor
```

### Monitoring & Maintenance

#### Real-time Monitoring
```bash
# Monitor all logs
tail -f logs/*.log

# Monitor system status
sudo systemctl status jira-monitor

# Monitor specific operations
tail -f logs/jira_integration.log | grep ERROR
```

#### Log Rotation
Automatic log rotation is built-in:
- 10MB maximum file size
- 5 backup files retained
- Compressed archival

#### Health Checks
```bash
# Check if dashboard is responding
curl -f http://localhost:8080/

# Check Jira connectivity
python -c "from jira_integration import JiraClient; print(JiraClient().validate_connection())"

# Check data freshness
ls -la donation_platform_data/
```

### Performance Optimization
- **CPU**: Minimal usage during refresh cycles
- **Memory**: ~50-100MB typical usage
- **Disk**: Log rotation prevents unlimited growth
- **Network**: API calls every 5 minutes

## �🛠️ Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Found
```bash
# Error: Virtual environment not found
# Solution:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. Jira Authentication Failed
```bash
# Error: 401 Unauthorized
# Solution: Check config.py
JIRA_EMAIL = "correct-email@example.com"
JIRA_API_TOKEN = "valid-token-here"
```

#### 3. Port Already in Use
```bash
# Error: Port 8080 is already in use
# Solution:
python run_pipeline.py --stop  # Stop existing servers
# Or use different port in dashboard_server.py
```

#### 4. No Data Displayed
```bash
# Check data files exist:
ls donation_platform_data/
# If missing, run:
python jira_integration.py
```

### Debugging Steps

1. **Test Jira Connection**
   ```bash
   python jira_integration.py
   ```

2. **Verify Configuration**
   ```bash
   python -c "import config; print(config.JIRA_BASE_URL)"
   ```

3. **Check Log Files**
   ```bash
   # Check all logs
   tail -f logs/*.log
   
   # Check specific component logs
   tail -f logs/jira_integration.log
   tail -f logs/pipeline.log
   ```

4. **Manual Dashboard Test**
   ```bash
   python dashboard_server.py
   ```

### Log Analysis
- **DEBUG**: Detailed tracing information for development
- **INFO**: Normal operation messages and status updates
- **WARNING**: Non-critical issues that don't stop execution
- **ERROR**: Critical issues that may cause failures

### Production Troubleshooting
```bash
# Monitor service status
sudo systemctl status jira-monitor

# View service logs
sudo journalctl -u jira-monitor -f

# Check application logs
tail -f /opt/jira-monitor/logs/pipeline.log

# Restart service if needed
sudo systemctl restart jira-monitor
```

---

## 📁 Additional Documentation

- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)**: Comprehensive logging system documentation
- **[EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)**: Detailed execution instructions  
- **[OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)**: Performance and optimization details

---

**Built with ❤️ for efficient Jira monitoring and DataDog integration**
- **SUCCESS**: Confirmation of successful operations

## 📝 Development Notes

### Code Reusability Principles
- **Modular Functions**: Each function has single responsibility
- **Configuration Driven**: Behavior controlled via `config.py`
- **Error Handling**: Consistent error handling patterns
- **Documentation**: Comprehensive inline documentation

### Extension Points
- **Storage Backends**: Add new storage options in `jira_integration.py`
- **Dashboard Themes**: Modify `unified_dashboard.html`
- **API Endpoints**: Add new endpoints in `dashboard_server.py`
- **Data Sources**: Integrate additional APIs following Jira pattern

### Performance Considerations
- **API Rate Limiting**: Respects Jira API limits
- **Memory Management**: Efficient data handling for large datasets
- **Caching Strategy**: File-based caching with timestamp validation
- **Background Processing**: Non-blocking auto-refresh operations

---

## 📞 Support

For issues or questions:
1. Check this README for common solutions
2. Review log files for error details
3. Test individual components in isolation
4. Verify Jira API connectivity and credentials

---

**System Status**: Production Ready  
**Last Updated**: August 13, 2025  
**Version**: 1.0.0
