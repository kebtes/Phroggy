import typing
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_link_group_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Connect", callback_data="link_group:connect"),
                InlineKeyboardButton(text="Exit", callback_data="link_group:exit")
            ]
        ]
    )

def create(buttons: typing.List, per_row: int = 2):
    """
    Creates a custom InlineKeyboard.

    Buttons should be in the form [[button_name, callback_str]]
    """
    per_row = min(3, per_row)

    keyboard = []
    for i in range(0, len(buttons), per_row):
        row = [InlineKeyboardButton(text=btn, callback_data=cb) for btn, cb in buttons[i: i + per_row]]
        keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
