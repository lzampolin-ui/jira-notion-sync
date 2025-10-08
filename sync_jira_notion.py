import os
import requests
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

# Fetch issues from Jira
def fetch_jira_issues():
    print("📋 Fetching issues from Jira...")
    url = f"{JIRA_URL}/rest/api/3/search"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    
    params = {
        "jql": JQL_QUERY,
        "maxResults": 100,
        "fields": "summary,status,description,created,updated,assignee,priority,customfield_10644"
    }
    
    response = requests.get(url, headers=headers, params=params, auth=auth)
    
    if response.status_code != 200:
        print(f"❌ Error fetching from Jira: {response.status_code}")
        print(response.text)
        return []
    
    data = response.json()
    issues = data.get('issues', [])
    print(f"✅ Found {len(issues)} issues in Jira")
    return issues

# Check if page already exists in Notion
def find_existing_page(jira_key):
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "filter": {
            "property": "tickets",
            "title": {
                "contains": jira_key
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        results = response.json().get('results', [])
        return results[0]['id'] if results else None
    return None

# Create or update page in Notion
def sync_to_notion(issue):
    jira_key = issue['key']
    fields = issue['fields']
    
    print(f"  📝 Syncing {jira_key}...")
    
    # Prepare Notion page properties
    properties = {
        "tickets": {
            "title": [
                {
                    "text": {
                        "content": f"{jira_key}: {fields.get('summary', 'No title')}"
                    }
                }
            ]
        },
        "Status": {
            "select": {
                "name": fields.get('status', {}).get('name', 'Unknown')
            }
        },
        "Client": {
            "rich_text": [
                {
                    "text": {
                        "content": "US BANGLA"
                    }
                }
            ]
        },
        "Priority": {
            "select": {
                "name": fields.get('priority', {}).get('name', 'Medium')
            }
        },
        "BT number": {
            "rich_text": [
                {
                    "text": {
                        "content": str(fields.get('customfield_10644', ''))
                    }
                }
            ]
        },
        "show to customer": {
            "checkbox": True
        }
    }
    
    # Check if page already exists
    existing_page_id = find_existing_page(jira_key)
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    if existing_page_id:
        # Update existing page
        url = f"https://api.notion.com/v1/pages/{existing_page_id}"
        data = {"properties": properties}
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"  ✅ Updated {jira_key} in Notion")
        else:
            p
