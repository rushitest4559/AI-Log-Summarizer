import json
import os
from collections import Counter

def filter_azure_logs(input_file="logs/azure_logs_24h.json", output_file="logs/azure_logs_filtered_24hrs.md"):
    """
    Aggressively filters Azure logs to minimize size.
    Groups identical operations by user and status to save space for AI analysis.
    """
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        # Use counters to group identical noise
        critical_summary = Counter()
        write_summary = Counter()
        general_summary = Counter()

        for log in logs:
            # Extract core details
            caller = log.get('caller', 'Unknown').split('/')[-1] # Shorter name
            op_obj = log.get('operationName', {})
            operation = op_obj.get('localizedValue', 'Unknown Op')
            op_value = op_obj.get('value', '').lower()
            status = log.get('status', {}).get('localizedValue', 'Status Unknown')
            level = log.get('level', 'Information')

            # Create a compact string for deduplication
            log_line = f"{caller} | {operation} ({status})"

            # 1. Critical/Failed (Priority 1)
            if level in ['Critical', 'Error', 'Warning'] or status == 'Failed':
                sub = log.get('subStatus', {}).get('localizedValue', '')
                line = f"{log_line} | Sub: {sub}" if sub else log_line
                critical_summary[line] += 1
            
            # 2. Write/Delete/Action (Priority 2)
            elif any(s in op_value for s in ['/write', '/delete', '/action']):
                write_summary[log_line] += 1
            
            # 3. Everything else (Priority 3)
            else:
                general_summary[log_line] += 1

        # Write ultra-compressed Markdown
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Azure Activity (Ultra-Compact)\n\n")

            if critical_summary:
                f.write("## ⚠️ FAILURES\n")
                for line, count in critical_summary.items():
                    f.write(f"- {line} | {count}x\n")
                f.write("\n")

            if write_summary:
                f.write("## 🛠️ CHANGES\n")
                for line, count in write_summary.items():
                    f.write(f"- {line} | {count}x\n")
                f.write("\n")

            if general_summary:
                f.write("## 🔍 READS/INFO\n")
                # Only show top noise to keep it small
                for line, count in general_summary.most_common(15):
                    f.write(f"- {line} | {count}x\n")

        print(f"✅ Aggressive filtering complete: {output_file}")

    except Exception as e:
        print(f"❌ Filtering failed: {e}")

if __name__ == "__main__":
    filter_azure_logs()