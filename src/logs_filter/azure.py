import json
import os
from collections import Counter

def filter_azure_logs(input_file="logs/azure_logs_24h.json", output_file="logs/azure_logs_filtered_24hrs.md"):
    """Reads raw Azure logs, extracts key status/operations, and writes a Markdown summary."""
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    try:
        # Use encoding="utf-8" to avoid the charmap error
        with open(input_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        critical_events = [] # Failures/Warnings
        write_events = []    # Create/Delete/Update/Action
        info_events = []     # Routine/Success noise

        for log in logs:
            caller = log.get('caller', 'Unknown')
            operation = log.get('operationName', {}).get('localizedValue', 'Unknown Operation')
            status = log.get('status', {}).get('localizedValue', 'Unknown Status')
            level = log.get('level', 'Information')
            timestamp = log.get('eventTimestamp', '')

            # 1. Capture Failures/Errors
            if level in ['Critical', 'Error', 'Warning'] or status == 'Failed':
                sub_status = log.get('subStatus', {}).get('localizedValue', '')
                critical_events.append(f"{timestamp} | {caller} | {operation} | **{status}** ({sub_status})")
                continue

            # 2. Capture Write/Action operations (Change events)
            # Azure operation names usually end in /write, /delete, or /action
            op_name_raw = log.get('operationName', {}).get('value', '')
            if any(suffix in op_name_raw.lower() for suffix in ['/write', '/delete', '/action']):
                write_events.append(f"{timestamp} | {caller} | {operation} | {status}")
            else:
                # 3. Informational Noise
                info_events.append(f"{caller} -> {operation} ({status})")

        # Deduplicate informational noise
        info_counts = Counter(info_events)

        # Write to Markdown File
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Azure Activity Summary (Last 24 Hours)\n\n")

            # Section: Critical / Failed Operations
            if critical_events:
                f.write("## ⚠️ Critical Alerts & Failures\n")
                for ev in critical_events:
                    f.write(f"- {ev}\n")
                f.write("\n")

            # Section: Resource Modifications
            f.write("## 🛠️ Resource Changes & Actions\n")
            if write_events:
                # Use set to remove identical duplicates if they exist
                for ev in sorted(list(set(write_events)), reverse=True):
                    f.write(f"- {ev}\n")
            else:
                f.write("- No resource changes (Write/Delete) detected.\n")
            f.write("\n")

            # Section: General Activity
            f.write("## 📊 General Activity\n")
            if info_counts:
                f.write("| Operation Detail | Repetitions |\n")
                f.write("| :--- | :--- |\n")
                for action, count in info_counts.items():
                    f.write(f"| {action} | {count}x |\n")
            else:
                f.write("- No general activity logs.\n")

        print(f"✅ Azure filtered summary saved to {output_file}")

    except Exception as e:
        print(f"❌ Azure filtering failed: {e}")

if __name__ == "__main__":
    filter_azure_logs()