import json
import os
from collections import Counter

def filter_aws_logs(input_file="logs/aws_logs_24h.json", output_file="logs/aws_logs_filtered_24hrs.md"):
    """Reads raw AWS logs, deduplicates noise, and writes a concise Markdown summary."""
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # Containers for filtering
        read_events = []
        write_events = []
        errors = []

        for log in logs:
            # Parse the inner CloudTrailEvent string for deeper details
            ct_event = json.loads(log.get('CloudTrailEvent', '{}'))
            
            # 1. Capture Errors (Most important)
            error_code = ct_event.get('errorCode')
            if error_code:
                errors.append({
                    "time": log.get('EventTime'),
                    "user": log.get('Username'),
                    "action": log.get('EventName'),
                    "error": error_code,
                    "msg": ct_event.get('errorMessage')
                })
                continue

            # 2. Separate Write vs Read
            # High priority: Actions that change things (ReadOnly: "false")
            if str(log.get('ReadOnly')).lower() == "false":
                write_events.append(f"{log.get('EventTime')} | {log.get('Username')} | {log.get('EventName')}")
            else:
                # Noise: Background read actions (Describe, List, Get)
                read_events.append(f"{log.get('Username')} -> {log.get('EventName')}")

        # 3. Deduplicate Read Events (The Noise)
        read_counts = Counter(read_events)

        # 4. Write to Markdown File
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# AWS Activity Summary (Last 24 Hours)\n\n")

            # Section: Security Alerts / Errors
            if errors:
                f.write("## ⚠️ Errors & Security Alerts\n")
                for err in errors:
                    f.write(f"- **{err['error']}**: User `{err['user']}` failed `{err['action']}` ({err['msg']})\n")
                f.write("\n")

            # Section: Resource Changes (Write Actions)
            f.write("## 🛠️ Resource Changes (Write Actions)\n")
            if write_events:
                for event in set(write_events): # Use set to avoid identical duplicates
                    f.write(f"- {event}\n")
            else:
                f.write("- No resource changes detected.\n")
            f.write("\n")

            # Section: Background Activity (Deduplicated)
            f.write("## 📊 Background Activity (Read-Only)\n")
            f.write("| Action Detail | Repetitions |\n")
            f.write("| :--- | :--- |\n")
            for action, count in read_counts.items():
                f.write(f"| {action} | {count}x |\n")

        print(f"✅ Filtered summary saved to {output_file} ({len(logs)} logs reduced to concise summary)")

    except Exception as e:
        print(f"❌ Filtering failed: {e}")

if __name__ == "__main__":
    filter_aws_logs()