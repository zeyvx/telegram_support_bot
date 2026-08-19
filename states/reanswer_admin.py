from aiogram.fsm.state import State, StatesGroup


class ReAnswer(StatesGroup):
    answer = State()
