import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# GOOGLE SHEET CONFIG
# ----------------------------
SHEET_ID = os.getenv("SHEET_ID")
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")

# ----------------------------
# SENDGRID CONFIG
# ----------------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_TO = os.getenv("MAIL_TO")

# ----------------------------
# MODE (Only PROD allowed now)
# ----------------------------
MODE = "PROD"   # No TEST mode anymore
