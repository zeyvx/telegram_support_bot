from aiogram.fsm.state import State, StatesGroup

class AdminReply(StatesGroup):
    waiting_for_reply = State()
    waiting_for_cancel_reason = State()