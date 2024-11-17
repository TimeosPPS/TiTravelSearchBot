from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class origin_pois(CallbackData, prefix="poits", sep=';'):
    action: str
def origin_button():
    builder = InlineKeyboardBuilder()

    pois_int_button = origin_pois(action='poits')
    builder.button(text="Список точок інтересу", callback_data=pois_int_button.pack())

    return_button = origin_pois(action='end')
    builder.button(text="Вказати інше місце", callback_data=return_button.pack())

    builder.adjust(2)
    return builder.as_markup()

def return_button():
    builder = InlineKeyboardBuilder()

    back_button = origin_pois(action='end')
    builder.button(text="Вказати інше місце", callback_data=back_button.pack())

    builder.adjust(2)
    return builder.as_markup()

def pois_buttons(pois_list):
    builder = InlineKeyboardBuilder()

    for i in pois_list.keys():
        builder.button(text=i, callback_data=i)

    builder.adjust(1)
    return builder.as_markup()

