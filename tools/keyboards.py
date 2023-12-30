from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(text="📊 Статистика", callback_data="statistic"),
        InlineKeyboardButton(text="🎬 Добавить фильм", callback_data="add_film"),
        InlineKeyboardButton(text="⛔ Удалить фильм", callback_data="delete_film"),
        InlineKeyboardButton(text="🔐 Выдать права", callback_data="give_permission"),
        InlineKeyboardButton(text="🌐 Панель каналов", callback_data="channels_panel")
    ]

    for button in buttons:
        builder.row(button)

    builder.adjust(2)

    return builder


def get_film_keyboard(back_callback) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(text="🔎 Код", callback_data="goto_id"),
        InlineKeyboardButton(text="🏷️ Название", callback_data="goto_title"),
        InlineKeyboardButton(text="📝 Описание", callback_data="goto_description"),
        InlineKeyboardButton(text="✅ Создать фильм", callback_data="create_film"),
        InlineKeyboardButton(text="↩️ Назад", callback_data=back_callback)
    ]

    for button in buttons:
        builder.row(button)

    return builder


def get_create_film_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    buttons = [
        InlineKeyboardButton(text="🧩 Создать", callback_data="finally_create"),
        InlineKeyboardButton(text="↩️ Назад", callback_data="add_film")
    ]

    for button in buttons:
        builder.row(button)

    return builder


def back_button(callback) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data=callback))

    return builder


def permissions_buttons(callback_admin, callback_take) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🧩 Назначить администратором", callback_data=callback_admin))
    builder.row(InlineKeyboardButton(text="❌ Забрать права", callback_data=callback_take), InlineKeyboardButton(text="↩️ Назад", callback_data='back'))

    return builder


def channels_panel_buttons(back_btn_callback) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="✅ Добавить канал", callback_data='add_channel'))
    builder.row(InlineKeyboardButton(text="❌ Убрать канал", callback_data='delete_channel'), InlineKeyboardButton(text="↩️ Назад", callback_data=back_btn_callback))

    return builder


def channels_generate(invites: list) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    for invite in invites:
        print(invite['title'])
        builder.row(InlineKeyboardButton(text=invite['title'],
                                         url=invite['invite']))

    return builder
