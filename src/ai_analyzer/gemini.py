import os
from typing import Optional

# Gemini SDK support
try:
    from google import genai as new_genai
    USE_NEW_GENAI = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_GENAI = False

def ask_gemini(
    aws_file: str = "logs/aws_logs_filtered_24hrs.md", 
    azure_file: str = "logs/azure_logs_filtered_24hrs.md"
) -> str:
    """Reads filtered markdown logs and sends them to Gemini for a security report."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        return "❌ GOOGLE_API_KEY missing in .env"

    # 1. Read the filtered files
    context = ""
    try:
        if os.path.exists(aws_file):
            with open(aws_file, "r", encoding="utf-8") as f:
                context += f"\n--- AWS FILTERED LOGS ---\n{f.read()}"
        
        if os.path.exists(azure_file):
            with open(azure_file, "r", encoding="utf-8") as f:
                context += f"\n--- AZURE FILTERED LOGS ---\n{f.read()}"
    except Exception as e:
        return f"❌ Error reading filtered files: {e}"

    if not context:
        return "ℹ️ No activity logs found to analyze."

    # 2. Construct the Prompt
    prompt = (
        "You are a Cloud Security Expert. Analyze these filtered activity logs from the last 24 hours. "
        "Provide a concise summary for a daily email report. Include:\n"
        "1. **Critical Alerts**: Highlight any errors, unauthorized attempts, or failures.\n"
        "2. **Resource **: Summarize major 'Write' or 'Delete' actions.\n"
        "3. **User Activity**: Identify the most active users and if their behavior looks normal.\n"
        "Keep the response professional and short for a mobile email view.\n\n"
        f"DATA:\n{context}"
    )

    # 3. Call AIChanges
    try:
        if USE_NEW_GENAI:
            client = new_genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-3-flash-preview", # Updated to current stable flash model
                contents=prompt
            )
            return response.text
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"❌ AI Error: {str(e)[:100]}"