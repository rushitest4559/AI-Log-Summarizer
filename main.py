#!/usr/bin/env python3
"""Daily Cloud Logs Monitor - Fetch, analyze, notify."""
import argparse
import os
from dotenv import load_dotenv

# Import modules
from src.log_fetchers.azure import fetch_azure_activity_logs
from src.log_fetchers.aws import fetch_aws_cloudtrail_logs
from src.logs_filter.aws import filter_aws_logs
from src.logs_filter.azure import filter_azure_logs
from src.ai_analyzer.gemini import ask_gemini
from src.notifier.email import send_email

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Daily Cloud Logs Monitor")
    parser.add_argument('--email', help="Recipient email address for the summary")
    parser.add_argument('--summary-only', action='store_true', help="Print only AI summary and exit")
    args = parser.parse_args()
    
    # -----------------------------------------------------------------------------
    # 1. Fetch Raw Logs
    # -----------------------------------------------------------------------------
    print("🔍 Step 1: Fetching raw logs from Cloud Providers...")
    aws_raw = fetch_aws_cloudtrail_logs()
    azure_raw = fetch_azure_activity_logs()
    
    print(f"✅ AWS: Received {len(aws_raw)} events")
    print(f"✅ Azure: Received {len(azure_raw)} events")

    # -----------------------------------------------------------------------------
    # 2. Filter & Deduplicate Logs
    # -----------------------------------------------------------------------------
    print("\n🧹 Step 2: Filtering and deduplicating logs to remove noise...")
    try:
        filter_aws_logs()
        filter_azure_logs()
        print("✅ Logs filtered and saved as Markdown summaries.")
    except Exception as e:
        print(f"❌ Critical Error during filtering: {e}")
        return

    # -----------------------------------------------------------------------------
    # 3. AI Analysis
    # -----------------------------------------------------------------------------
    print("\n🤖 Step 3: Sending filtered data to Gemini for analysis...")
    # ask_gemini now reads from the .md files automatically
    summary = ask_gemini()
    
    if args.summary_only:
        print("\n--- AI SUMMARY ---")
        print(summary)
        return
    
    print("\n--- AI Analysis Result ---")
    print(summary)
    
    # -----------------------------------------------------------------------------
    # 4. Send Notification
    # -----------------------------------------------------------------------------
    if args.email:
        print(f"\n📧 Step 4: Sending summary to {args.email}...")
        result = send_email(summary, args.email)
        
        if result["success"]:
            print("✅ Email sent successfully!")
        else:
            print(f"❌ Email failed: {result['error']}")
    else:
        print("\nℹ️  Skipping email (use --email <address> to send reports).")

if __name__ == "__main__":
    main()