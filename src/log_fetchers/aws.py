import boto3
import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def fetch_aws_cloudtrail_logs(region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """Fetch all AWS CloudTrail events for last 24h and save to file."""
    cloudtrail = boto3.client('cloudtrail', region_name=region)
    
    # 1. Setup Time and File Path
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=24)
    output_file = "logs/aws_logs_24h.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    all_logs = []
    next_token = None
    
    

    try:
        with open(output_file, "w") as f:
            f.write("[\n")  # Start JSON array
            first_entry = True
            
            while True:
                # 2. Fetch batch from AWS
                lookup_params = {
                    'StartTime': start_time,
                    'EndTime': end_time,
                    'MaxResults': 50  # Max batch size for LookupEvents
                }
                if next_token:
                    lookup_params['NextToken'] = next_token
                
                print(f"📡 Fetching batch from AWS {region}...")
                response = cloudtrail.lookup_events(**lookup_params)
                events = response.get('Events', [])
                
                # 3. Process batch and write to file
                for event in events:
                    # Convert datetime objects to string for JSON compatibility
                    event_copy = event.copy()
                    if 'EventTime' in event_copy:
                        event_copy['EventTime'] = event_copy['EventTime'].isoformat()
                    
                    all_logs.append(event_copy)
                    
                    if not first_entry:
                        f.write(",\n")
                    json.dump(event_copy, f)
                    first_entry = False
                
                # 4. Check for more data
                next_token = response.get('NextToken')
                if not next_token:
                    break
            
            f.write("\n]")  # Close JSON array
            
        print(f"✅ Successfully saved {len(all_logs)} AWS logs to {output_file}")
        return all_logs

    except Exception as e:
        print(f"❌ Error during AWS fetch/save: {e}")
        return all_logs