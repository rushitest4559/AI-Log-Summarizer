import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

def send_email(summary: str, to_email: str, from_email: Optional[str] = None, smtp_server: str = 'smtp.gmail.com') -> dict:
    from_email = from_email or os.getenv('EMAIL_FROM')
    password = os.getenv('EMAIL_PASSWORD')
    
    # 1. Internal Validation
    if not from_email or not password:
        return {"success": False, "error": "Missing EMAIL_FROM or EMAIL_PASSWORD in .env"}

    msg = MIMEText(summary)
    msg['Subject'] = 'Daily Cloud Logs Summary'
    msg['From'] = from_email
    msg['To'] = to_email
    
    try:
        # timeout=10 prevents the script from hanging forever
        with smtplib.SMTP(smtp_server, 587, timeout=10) as server:
            server.starttls()
            
            # This is where your current password fail will be caught
            server.login(from_email, password) 
            
            server.send_message(msg)
            return {"success": True, "error": None}
            
    except smtplib.SMTPAuthenticationError as e:
        return {"success": False, "error": f"Invalid Password. Use a Gmail App Password (16 chars). {e}"}
    except smtplib.SMTPConnectError:
        return {"success": False, "error": "Could not connect to SMTP server. Check your internet."}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

