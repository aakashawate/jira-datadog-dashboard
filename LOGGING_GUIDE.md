# Logging System Documentation

## Overview
The Jira monitoring system now includes a comprehensive production-ready logging infrastructure designed for Linux server deployment. This logging system provides detailed tracking, debugging capabilities, and error monitoring across all system components.

## Features

### 1. Multi-Logger Architecture
- **Separate loggers for each module**: jira_integration, dashboard_server, pipeline, system_utils, system_critical
- **Hierarchical logging**: Each component has its own log file for focused debugging
- **Centralized configuration**: All logging configured through utils.py Logger class

### 2. Production-Ready Configuration
- **Rotating file handlers**: Automatic log rotation at 10MB with 5 backup files
- **Multiple log levels**: DEBUG, INFO, WARNING, ERROR with appropriate filtering
- **Detailed formatting**: Timestamp, logger name, level, filename, line number, and message
- **Exception tracking**: Full stack traces with exc_info=True for comprehensive error analysis

### 3. Log Files Structure
```
logs/
├── jira_integration.log    # Jira API interactions, data fetching, project sync
├── dashboard_server.log    # Web server operations, HTTP requests, auto-refresh
├── pipeline.log           # Main orchestration, startup, monitoring cycles
├── system_utils.log       # System operations, environment checks, process management
└── system_critical.log    # Critical system events, failures, shutdowns
```

## Usage

### 1. Importing Logger
```python
from utils import Logger

# Get a logger for your module
logger = Logger.get_logger('your_module_name')
```

### 2. Logging Levels
```python
# Debug information (detailed tracing)
logger.debug("Detailed debugging information")

# General information (normal operation)
logger.info("Application started successfully")

# Warning conditions (potential issues)
logger.warning("Configuration file missing, using defaults")

# Error conditions (operation failed)
logger.error("Failed to connect to Jira API")

# Exception logging with full stack trace
try:
    # some operation
    pass
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

### 3. Enhanced Modules
All core modules now include comprehensive logging:

#### jira_integration.py
- API connection validation
- Project and issue fetching progress
- Data processing statistics
- Error handling with detailed API responses

#### dashboard_server.py
- HTTP request logging
- Auto-refresh cycle tracking
- Data loading and processing
- Server startup and shutdown events

#### run_pipeline.py
- Pipeline orchestration steps
- Environment validation
- Component startup/shutdown
- Monitoring cycle tracking

#### utils.py SystemUtils
- Virtual environment checks
- Process management operations
- System information gathering
- Cross-platform compatibility logging

## Deployment Benefits

### 1. Linux Server Deployment
- **Log file monitoring**: Easily monitor application health with `tail -f logs/*.log`
- **Issue diagnosis**: Detailed logs help identify problems in production
- **Performance tracking**: Monitor API response times and system performance
- **Automated monitoring**: Log files can be integrated with monitoring tools

### 2. Production Monitoring
```bash
# Monitor all logs in real-time
tail -f logs/*.log

# Monitor specific component
tail -f logs/jira_integration.log

# Search for errors across all logs
grep -r "ERROR" logs/

# Monitor system critical events
tail -f logs/system_critical.log
```

### 3. Log Rotation
- Automatic rotation prevents disk space issues
- 5 backup files ensure sufficient history
- 10MB rotation size balances detail and storage

## Integration Examples

### 1. Error Tracking
```python
# In jira_integration.py
try:
    response = self.session.get(url)
    response.raise_for_status()
    logger.info(f"Successfully fetched {len(issues)} issues")
except requests.exceptions.RequestException as e:
    logger.error(f"HTTP error: {str(e)}")
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f"Response status: {e.response.status_code}")
        logger.error(f"Response text: {e.response.text[:500]}")
```

### 2. Performance Monitoring
```python
# In dashboard_server.py
start_time = time.time()
# ... operation ...
duration = time.time() - start_time
logger.info(f"Data refresh completed in {duration:.2f} seconds")
```

### 3. System Monitoring
```python
# In run_pipeline.py
logger.info(f"Auto-refresh cycle #{refresh_count} started")
# ... refresh operation ...
logger.info(f"Auto-refresh cycle #{refresh_count} completed successfully")
```

## Testing the Logging System

The logging system is automatically tested during normal application operation. All modules include comprehensive logging that activates when you run the main pipeline:

```bash
# Test logging during normal operation
python run_pipeline.py

# Monitor logs to verify logging is working
tail -f logs/*.log
```

This will:
1. Create log entries for all modules during normal operation
2. Test all log levels (DEBUG, INFO, WARNING, ERROR) through real application flow
3. Test exception logging with stack traces if any errors occur
4. Verify log file creation and rotation in the logs/ directory

## Maintenance

### 1. Log File Management
- Log files are automatically rotated at 10MB
- 5 backup files are maintained per logger
- Old log files are compressed and archived

### 2. Log Level Configuration
- Default level is INFO for production
- Change to DEBUG for detailed troubleshooting
- ERROR level for minimal logging in stable environments

### 3. Monitoring Integration
The logging system is designed to integrate with:
- Logstash/ELK stack
- Splunk
- System monitoring tools (Nagios, Zabbix)
- Cloud logging services (CloudWatch, Stackdriver)

## Benefits for Linux Deployment

1. **Real-time Monitoring**: `tail -f logs/pipeline.log` shows live system status
2. **Error Diagnosis**: Detailed error logs with stack traces for quick debugging
3. **Performance Tracking**: Monitor API response times and system performance
4. **Automated Alerting**: Log patterns can trigger alerts in monitoring systems
5. **Audit Trail**: Complete record of all system operations and changes
6. **Troubleshooting**: Detailed logs help resolve issues without access to console output
