# 🚀 Daily Cloud Security Monitor

An automated, AI-powered security auditor that scans **AWS CloudTrail** and **Azure Activity Logs** every 24 hours. It uses **OIDC (Keyless) Auth** for maximum security and **Gemini 3 Flash Preview** to distill thousands of logs into a high-density, actionable email report.

---

## Algorithm of script
- **Login into aws and azure using oidc**
- **fecthes logs from aws cloudtrail and azure activity logs of last 24 hours**
- **fetch logs in batches like fecth only 100 logs at a time and immediately write it into files aws_logs_24h.json and azure_logs_24h.json**
- **filter logs into aws_logs_filtered_24h.md and azure_logs_filtered_24h.md files, it does not filters out rows but it identify patterns and write patterns in this .md files**
- **send this files (aws_logs_filtered_24h.md and azure_logs_filtered_24h.md) to gemini free ai api model and generate summary from this filtered logs**
- **send this summary to recipient mail**  

---

## 📺 Project Walkthrough

[![Watch the Demo]](https://youtu.be/lP4XYvb5oPo)  

---

## ✨ Key Features

- **Multi-Cloud:** Unified reporting for AWS and Azure.
- **OIDC Security:** No long-lived credentials; uses GitHub Actions as a trusted identity provider.
- **AI Log Compression:** Aggressive filtering reduces "log noise" by 90% before analysis, saving tokens and costs.
- **Daily Automation:** Fully automated via GitHub Actions Cron.

---

## 🛠️ Tech Stack

- **Cloud:** AWS (CloudTrail, IAM), Azure (Monitor, Entra ID)
- **AI:** Google Gemini 3 Flash
- **CI/CD:** GitHub Actions (OIDC + Python)
- **Logic:** Python (Boto3, Azure-SDK)

---

## Run this script in your Laptop
1. Clone the repo
2. If you want to run this only for AWS then you must have aws configure already done in your laptop and you have cloudtrail logs view access for us-east-1. If you only want to run this for azure then you must have az login already done in your laptop and you have access of view azure activity logs. For both aws and azure you must have az login and aws configure already done in command line before running this script.
3. For only aws logs summary comment the line no 28, 31, 39 in main.py and for only azure comment the line no 29, 32, 40 in main.py, If you want summary for both your aws and azure accounts then don't comment anything.
4. Create .env file in root folder of project and write this environment variables: GOOGLE_API_KEY, AZURE_SUBSCRIPTION_ID, AZURE_TENANT_ID, EMAIL_FROM, EMAIL_PASSWORD. 
5. GOOGLE_API_KEY, EMAIL_FROM, EMAIL_PASSWORD(16 chars email app password not email password), this 3 env variables are mandatory, if you don't want summary of azure then you can comment the lines in main.py (step 3) and ignore this 2 variables.
6. GOOGLE_API_KEY generated from google ai studio website which is completely free because free tier is enough for this project.
7. Ensure you have python in your laptop and run pip install requirements.txt
8. RUN python main.py --email "type email where you want to recieve ai summary"
9. Open your email and see the summary.

---

## RUN this script daily automatically at free of cost
1. Fork this repo
2. Add this environment variables in your repo settings as repo secrets: EMAIL_FROM, EMAIL_PASSWORD, GOOGLE_API_KEY, RECIPIENT_EMAIL. 
3. For only aws logs summary comment the line no 28, 31, 39 in main.py and for only azure comment the line no 29, 32, 40 in main.py, If you want summary for both your aws and azure accounts then don't comment anything. For only aws skip the 5th step and for only azure skip the 4th step. For only aws comment the lines 29 to 34 in daily-logs.yml file and for only azure comment the lines 23 to 27 in daily-logs.yml file.
4. For AWS, login into aws account, create identity provider for this github actions and create role with Cloudtrail read policy (get help of ai how to create identity provider and attach role for github actions to view cloudtrial logs). Create one more secret in github repo settings AWS_ROLE_ARN and paste the role arn which you created in aws console.
5. For AZURE create entra id app with federated credentials (get help of ai how to setup oidc for github actions in azure) and create 3 more secrets in github repo settings AZURE_CLIENT_ID, AZURE_SUBSCRIPTION_ID, AZURE_TENANT_ID. 
6. After setting this variables correctly, wait for night 12 am and you get sumary of what happen in your aws and azure account automatically absolutely free of cost.

## 🤝 Connect With Me

If you found this helpful, let's connect! I post about cloud security and AI automation regularly.

[**Check out my post about this on LinkedIn**](https://www.linkedin.com/in/rushikesh-nikam-11637033a/)

---