import os
import requests
import traceback
from datetime import datetime

# Configuration from environment variables
JIRA_URL = os.environ.get('JIRA_URL')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

JQL_QUERY = '''project = "GMI"
AND "client" = "US BANGLA"
AND status NOT IN (Completed, REJECTED, ROLLBACKED)
AND "show to customer" = Yes
ORDER BY "cf[10644]" ASC, created DESC'''

print("🚀 Starting Jira to Notion sync...")
print(f"JIRA_URL: {JIRA_URL}")
print(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")

# Fetch issues from Jira
def fetch_jira_issues():
    try:
        print("📋 Fetching issues from Jira...")
        url = f"{JIRA_URL}/rest/
