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
        url = f"{JIRA_URL}/rest/api/3/search/jql"
        auth = (JIRA_EMAIL, JIRA_API_TOKEN)
        headers = {"Accept": "application/json"}
        
        params = {
            "jql": JQL_QUERY,
            "maxResults": 100,
            "fields": "summary,status,description,created,updated,assignee,priority,customfield_10644"
        }
        
        print(f"Making request to: {url}")
        response = requests.get(url, headers=headers, params=params, auth=auth)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Error fetching from Jira: {response.status_code}")
            print(f"Response: {response.text}")
            return []
        
        data = response.json()
        issues = data.get('issues', [])
        print(f"✅ Found {len(issues)} issues in Jira")
        
        # Print first issue for debugging
        if issues:
            print(f"First issue: {issues[0]['key']}")
        
        return issues
    except Exception as e:
        print(f"❌ Exception in fetch_jira_issues: {str(e)}")
        traceback.print_exc()
        return []

# Check if page already exists in Notion
def find_existing_page(jira_key):
    try:
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        data = {
            "filter": {
                "property": "Tickets",
                "title": {
                    "contains": jira_key
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return results[0]['id'] if results else None
        else:
            print(f"  ⚠️  Error checking existing page: {response.status_code}")
            print(f"  {response.text}")
        return None
    except Exception as e:
        print(f"  ❌ Exception in find_existing_page: {str(e)}")
        return None

# Create or update page in Notion
def sync_to_notion(issue):
    try:
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
            "show to customer": {
                "checkbox": True
            }
        }
        
        # Add Priority if it exists
        if fields.get('priority'):
            properties["Priority"] = {
                "select": {
                    "name": fields['priority']['name']
                }
            }
        
        # Add BT number if it exists
        if fields.get('customfield_10644'):
            properties["BT number"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": str(fields['customfield_10644'])
                        }
                    }
                ]
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
                print(f"  ❌ Error updating {jira_key}: {response.status_code}")
                print(f"  {response.text}")
        else:
            # Create new page
            url = "https://api.notion.com/v1/pages"
            data = {
                "parent": {"database_id": NOTION_DATABASE_ID},
                "properties": properties
            }
            
            print(f"  Creating page with data: {data}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"  ✅ Created {jira_key} in Notion")
            else:
                print(f"  ❌ Error creating {jira_key}: {response.status_code}")
                print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  ❌ Exception in sync_to_notion: {str(e)}")
        traceback.print_exc()

# Main execution
def main():
    try:
        issues = fetch_jira_issues()
        
        if not issues:
            print("⚠️  No issues found or error occurred")
            return
        
        print(f"\n🔄 Syncing {len(issues)} issues to Notion...")
        
        for issue in issues:
            sync_to_notion(issue)
        
        print("\n✨ Sync completed!")
    except Exception as e:
        print(f"❌ Fatal error in main: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
