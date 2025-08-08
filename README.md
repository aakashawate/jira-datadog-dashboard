# Jira to Database Integration

Ultra-simple, single-file solution for syncing Jira issues to MySQL database.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Credentials
Edit line 24-34 in `jira_integration.py`:

```python
# UPDATE THESE CREDENTIALS
JIRA_BASE_URL = "https://yourcompany.atlassian.net"
JIRA_EMAIL = "your.email@company.com" 
JIRA_API_TOKEN = "your_api_token_here"
JIRA_PROJECT_ID = "your_project_id"

DB_HOST = "localhost"
DB_USERNAME = "jira_user"
DB_PASSWORD = "your_password"
DB_DATABASE = "jira_monitoring"
```

### 3. Run
```bash
python jira_integration.py --setup  # First time
python jira_integration.py          # Regular sync
```

## Files
- `jira_integration.py` - Complete application
- `requirements.txt` - Dependencies
- `README.md` - This guide

That's it! Just 3 files total.
