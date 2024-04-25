from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_call_btns_for_delete(*, sizes: tuple[int] == (1,), data):
    keyboard = InlineKeyboardBuilder()
    for app in data:
        keyboard.add(InlineKeyboardButton(text=app.name, callback_data=f'delete_{app.id}'))
    return keyboard.adjust(*sizes).as_markup()


def get_call_btns_get_app(*, sizes: tuple[int] == (1,), data):
    keyboard = InlineKeyboardBuilder()
    for app in data:
        keyboard.add(InlineKeyboardButton(text=app.name, callback_data=f'get_{app.id}'))
    return keyboard.adjust(*sizes).as_markup()
