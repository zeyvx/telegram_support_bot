from aiogram.fsm.state import State, StatesGroup

class AddAdmin(StatesGroup):
    admin_id = State()
    admin_role = State()
    admin_name = State()