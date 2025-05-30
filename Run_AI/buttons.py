from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def level():
    inline_kb_list = [
        [InlineKeyboardButton(text="Начинающий", callback_data="Начинающий")],
        [InlineKeyboardButton(text="Средний", callback_data="Средний")],
        [InlineKeyboardButton(text="Продвинутый", callback_data="Продвинутый")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def dif():
    inline_kb_list = [
        [InlineKeyboardButton(text="Увеличить нагрузки", callback_data="p")],
        [InlineKeyboardButton(text="Снизить нагрузки", callback_data="min")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)


def target():
    inline_kb_list = [
        [InlineKeyboardButton(text="Потеря лишнего веса", callback_data="low")],
        [InlineKeyboardButton(text="Поддержание формы", callback_data="mid")],
        [InlineKeyboardButton(text="Улучшение результатов", callback_data="up")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
