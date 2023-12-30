from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from aiogram.types import Message, CallbackQuery

from filters import its_admin, check_channels
from tools import database, keyboards

router = Router()


class UserStates(StatesGroup):
    search_film = State()


@router.message(
    CommandStart()
)
async def admin_start(message: Message, state: FSMContext) -> None:
    user = database.User.get_or_create(id=message.from_user.id)

    if user:
        is_admin = database.check_admin(message.from_user.id)

        if is_admin:
            await message.answer(
                text=f"Привет, {message.from_user.first_name}, ты находишься в админ панели, чем займемся сегодня?",
                reply_markup=keyboards.get_admin_keyboard().as_markup()
            )
            return

    await message.answer("Привет! Введи код чтобы получить название фильма и его краткое описание")
    await state.set_state(UserStates.search_film)


@router.callback_query(
    F.data == "statistic",
    its_admin.ItsAdmin()
)
async def admin_panel(callback: CallbackQuery) -> None:
    all_users = database.User.select().count()
    day_users = database.get_users_for_day()

    await callback.message.answer(
        text=f"<b>Статистика бота</b>\n\nПользователей за все время: <u>{all_users}</u>\nЗа этот день: <u>{day_users}</u>",
        parse_mode="HTML"
    )


@router.message(
    StateFilter(UserStates.search_film),
    F.text,
    check_channels.CheckChannels()
)
async def film_search(message: Message) -> None:
    film = database.Film.get_or_none(id=message.text)

    if film:
        await message.answer(
            f"Название фильма: {film.name}\n\nОписание: {film.description}",
        )
        return

    await message.answer(
        "Данный фильм отсутствует",
    )


# @router.message(
#     F.text
# )
# async def write_user(message: Message) -> None:
#     print(message.text)
#     database.User.get_or_create(id=message.from_user.id)
