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
    """Sends logs to Gemini for a high-density, low-token security summary."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key: return "❌ API_KEY missing"

    # 1. Load data
    context = ""
    for cloud, path in [("AWS", aws_file), ("Azure", azure_file)]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                context += f"\n[{cloud} LOGS]\n{f.read()}"

    if not context: return "ℹ️ No logs found."

    # 2. Ultra-short prompt for token efficiency
    prompt = (
        "Role: Cloud Security Expert. Task: Summarize logs concisely. "
        "Format: No bolding stars except headers. Use double spacing. "
        "Structure:\n"
        "## SUMMARY: 1-sentence overview.\n\n"
        "## AWS: Logins & Infra changes + Advice.\n\n"
        "## AZURE: Logins & Infra changes + Advice.\n\n"
        f"DATA:\n{context}"
    )

    # 3. Call AI
    try:
        model_id = "gemini-3-flash-preview" 
        if USE_NEW_GENAI:
            client = new_genai.Client(api_key=api_key)
            response = client.models.generate_content(model=model_id, contents=prompt)
            return response.text
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_id)
            response = model.generate_content(prompt)
            return response.text
    except Exception as e:
        return f"❌ AI Error: {str(e)[:50]}"