from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
OPERATOR_PHONE = getenv('OPERATOR_PHONE', '—')

ADMIN_PRIORITY = 1
SENIOR_ADMIN_PRIORITY = 2
MODERATOR_PRIORITY = 3
SUPER_ADMIN_PRIORITY = 4

_raw_super_admin_id = getenv('SUPER_ADMIN_ID')
if not _raw_super_admin_id:
    raise RuntimeError('SUPER_ADMIN_ID is not configured')

try:
    SUPER_ADMIN_ID = int(_raw_super_admin_id)
except ValueError as exc:
    raise RuntimeError('SUPER_ADMIN_ID must be an integer') from exc
