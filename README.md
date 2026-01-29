☁️ Daily Cloud Security Sentinel
An automated monitoring tool that fetches logs from AWS CloudTrail and Azure Activity Logs, uses Gemini AI to filter out background noise, and emails a concise security summary of the last 24 hours.

🚀 Features
Multi-Cloud Support: Integrated with AWS and Azure.

Smart Filtering: Reduces raw log noise (e.g., 350KB JSON → 8KB Markdown) to stay within AI context limits and save costs.

AI Analysis: Uses Google Gemini to identify suspicious patterns, unauthorized access attempts, and resource changes.

Automated Reporting: Sends a clean, professional security report via email.

🛠️ Setup & Local Usage
Clone the Repo:

Bash
git clone https://github.com/your-username/cloud-logs-monitor.git
cd cloud-logs-monitor
Install Dependencies:

Bash
pip install -r requirements.txt
Configure Environment: Create a .env file:

Code snippet
GOOGLE_API_KEY=your_gemini_api_key
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
AZURE_SUBSCRIPTION_ID=your_id
Run the Script:

Bash
python main.py --email your-recipient@example.com
🤖 GitHub Actions: Run Daily for Free
You don't need to run this manually. You can host it for free using GitHub Actions.

1. Fork this Repository
Click the Fork button at the top right of this page.

2. Configure Secrets
Go to Settings > Secrets and variables > Actions and add the following secrets:

GOOGLE_API_KEY: Your Gemini API key.

EMAIL_FROM & EMAIL_PASSWORD: Your sender credentials (use Gmail App Passwords).

AZURE_SUBSCRIPTION_ID: Your Azure sub ID.

RECIPIENT_EMAIL: Where you want the daily report sent.

3. Setup OIDC (Cloud Authentication)
To allow GitHub to talk to AWS/Azure without storing permanent keys:

For AWS: Create an IAM Role with a Trust Policy for GitHub Actions OIDC and attach ReadOnlyAccess.

For Azure: Register an App in Entra ID, add Federated Credentials for your GitHub branch, and assign the Reader role.

⚠️ Limitations & Security Notes
1. Regional Visibility (AWS)
Current Status: This script fetches logs primarily from us-east-1 and your specified primary region.

The Risk: "Shadow Infrastructure." A hacker could launch resources in an unused region (e.g., af-south-1) which this script might miss unless those regions are explicitly checked.

The Solution:

Option A: Enable Global Trail in AWS CloudTrail. This consolidates all regional logs into one S3 bucket, which the script can then read centrally.

Option B: Modify the script to iterate through all AWS regions (Note: This increases execution time and GitHub Runner usage).

2. AI Quota
Using the Free Tier of Gemini may result in 429 Resource Exhausted errors if the logs are too large or the script is run too frequently. Our filtering logic mitigates this, but high-activity accounts may require a paid Gemini tier.

🏗️ Project Architecture
The project is built with a modular approach:

Fetchers: Connect to Cloud APIs and download raw JSON.

Filters: Clean and deduplicate data into Markdown (MD) format.

Analyzer: Feeds MD files to Gemini AI with a security-focused prompt.

Notifier: Dispatches the final analysis via SMTP.