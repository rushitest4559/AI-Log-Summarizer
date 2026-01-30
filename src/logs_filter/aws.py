import json
import os
from collections import Counter

def filter_aws_logs(input_file="logs/aws_logs_24h.json", output_file="logs/aws_logs_filtered_24hrs.md"):
    """
    Aggressively compresses AWS CloudTrail logs.
    Focuses on 'Who did What' and 'How many times' instead of raw JSON.
    """
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            logs = json.load(f)

        error_summary = Counter()
        write_summary = Counter()
        read_summary = Counter()

        for log in logs:
            # Shorten username (remove full ARN paths if present)
            user = str(log.get('Username', 'Unknown')).split('/')[-1]
            event_name = log.get('EventName', 'UnknownEvent')
            
            # Extract error details from the inner JSON if it exists
            ct_event = json.loads(log.get('CloudTrailEvent', '{}'))
            error_code = ct_event.get('errorCode')
            
            # 1. Capture Errors (Highest Priority)
            if error_code:
                msg = ct_event.get('errorMessage', 'Denied')
                # Keep error message short
                compact_error = f"{user} | {event_name} | {error_code} ({msg[:50]})"
                error_summary[compact_error] += 1
                continue

            # 2. Resource Changes (ReadOnly: "false")
            if str(log.get('ReadOnly')).lower() == "false":
                change_line = f"{user} | {event_name}"
                write_summary[change_line] += 1
            
            # 3. Read Activity (Noise)
            else:
                read_line = f"{user} | {event_name}"
                read_summary[read_line] += 1

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# AWS Security Activity (Compressed)\n\n")

            if error_summary:
                f.write("## ⚠️ FAILURES & DENIALS\n")
                for line, count in error_summary.items():
                    f.write(f"- {line} | {count}x\n")
                f.write("\n")

            if write_summary:
                f.write("## 🛠️ INFRA CHANGES\n")
                # Grouping changes ensures one-line per action type
                for line, count in write_summary.items():
                    f.write(f"- {line} | {count}x\n")
                f.write("\n")

            if read_summary:
                f.write("## 🔍 DISCOVERY & READS\n")
                # Aggressively limit read noise to the top 10 most frequent
                for line, count in read_summary.most_common(10):
                    f.write(f"- {line} | {count}x\n")

        print(f"✅ Aggressive AWS filter complete: {output_file}")

    except Exception as e:
        print(f"❌ AWS Filtering failed: {e}")

if __name__ == "__main__":
    filter_aws_logs()