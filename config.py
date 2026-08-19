from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = getenv('BOT_TOKEN')
OPERATOR_PHONE = getenv('OPERATOR_PHONE', '—')

ADMIN_PRIORITY = 1
SENIOR_ADMIN_PRIORITY = 2
MODERATOR_PRIORITY = 3
SUPER_ADMIN_PRIORITY = 4

SUPER_ADMIN_ID = 0
super_admin_id = getenv('SUPER_ADMIN_ID')

if super_admin_id:
    try:
        SUPER_ADMIN_ID = int(super_admin_id)
    except ValueError:
        print('SUPER_ADMIN_ID должен быть числом')
