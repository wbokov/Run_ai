from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    waiting_for_weight = State()
    waiting_for_age = State()
    waiting_for_new_weight = State()
    waiting_for_times = State()
    waiting_for_times2 = State()
    waiting_data = State()
    waiting_for_ask = State()
    waiting_for_rate1 = State()
    waiting_for_rate2 = State()
    waiting_for_rate3 = State()
    waiting_for_admin = State()
