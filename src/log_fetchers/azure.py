import os
import requests
import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def fetch_azure_activity_logs(subscription_id: str = None) -> List[Dict[str, Any]]:
    """
    Fetches all logs for 24h, saves them directly to 'azure_logs_24h.json' 
    to save RAM, and returns the list to main.
    """
    subscription_id = subscription_id or os.getenv('AZURE_SUBSCRIPTION_ID')
    if not subscription_id:
        return []

    # 1. Get Access Token
    token_cmd = 'az account get-access-token --scope https://management.azure.com/.default --query accessToken --output tsv'
    token = os.popen(token_cmd).read().strip()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # 2. Set Time Range
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)

    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    filter_str = f"eventTimestamp ge '{start_str}' and eventTimestamp le '{end_str}'"
    
    # New, more stable URL
    url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Insights/eventtypes/management/values"
    
    # Move the API version and filter into params strictly
    params = {
        'api-version': '2015-04-01', # This older version is actually MORE stable for this specific endpoint
        '$filter': f"eventTimestamp ge '{start_str}' and eventTimestamp le '{end_str}'"
    }
    
    all_logs = []    
    output_file = "logs/azure_logs_24h.json"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    

    try:
        # Open file to write immediately
        with open(output_file, "w") as f:
            f.write("[\n") # Start JSON array
            first_entry = True
            
            while url:
                print(f"📡 Fetching batch from Azure...")
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                batch = data.get('value', [])
                for log in batch:
                    # Append to the return list (for main.py)
                    all_logs.append(log)
                    
                    # Write to file (for storage)
                    if not first_entry:
                        f.write(",\n")
                    json.dump(log, f)
                    first_entry = False
                
                # Pagination: Get next link
                url = data.get('nextLink')
                params = {} # nextLink has params built-in
                
            f.write("\n]") # Close JSON array

        print(f"✅ Successfully saved {len(all_logs)} logs to {output_file}")
        return all_logs

    except Exception as e:
        print(f"❌ Error during Azure fetch/save: {e}")
        return all_logs