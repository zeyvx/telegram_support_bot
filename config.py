from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
OPERATOR_PHONE = getenv("OPERATOR_PHONE")

ADMIN_IDS = getenv("ADMIN_IDS", "")
ADMINS = [int(admin_id.strip()) for admin_id in ADMIN_IDS.split(",") if admin_id.strip()]
