from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
OPERATOR_PHONE = getenv('OPERATOR_PHONE', '')

ADMIN_PRIORITY = 1
SENIOR_ADMIN_PRIORITY = 2
MODERATOR_PRIORITY = 3
SUPER_ADMIN = 4

_super_admin_id = getenv('SUPER_ADMIN_ID')
SUPER_ADMIN_ID = int(_super_admin_id) if _super_admin_id and _super_admin_id.isdigit() else 0
