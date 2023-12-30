from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData

from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on, After

from aiogram.types import Message, CallbackQuery

from aiogram.exceptions import TelegramBadRequest

from enum import Enum

from tools import database, keyboards

router = Router()


class Action(Enum):
    EXIT = 'exit'
    BACK = 'back'
    GOTO_WRITING = 'writing'


class ButtonsCB(CallbackData, prefix='buttons'):
    action: Action


class GivePermissionCB(CallbackData, prefix='permissions'):
    action: str
    user_id: int = None
    username: str = None


class NewFilm(Enum):
    id_film = 'id_film'
    title_film = 'title_film'
    description_film = 'description_film'


class Add_Film(Scene, state='new_film'):
    @on.callback_query.enter()
    async def add_film(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Начните создание нового фильма / сериала с того что вам будет удобно!",
            reply_markup=keyboards.get_film_keyboard(back_callback=ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.callback_query(F.data == 'goto_id', after=After.goto('writing_id'))
    async def goto_id(self, callback: CallbackQuery) -> None:
        pass

    @on.callback_query(F.data == 'goto_title', after=After.goto('title_film'))
    async def goto_title(self, callback: CallbackQuery) -> None:
        pass

    @on.callback_query(F.data == 'goto_description', after=After.goto('description_film'))
    async def goto_description(self, callback: CallbackQuery) -> None:
        pass

    @on.callback_query(F.data == 'create_film')
    async def create_film(self, callback: CallbackQuery, state: FSMContext) -> None:
        user_data = await state.get_data()
        code, title, description = (user_data.get('choosen_id', 'Отсутствует'),
                                    user_data.get('choosen_title', 'Отсутствует'),
                                    user_data.get('choosen_description', 'Отсутствует'))

        await callback.message.edit_text(
            text="Данные о фильме:\n\n"
                 f"Код: {code}\n"
                 f"Название: {title}\n"
                 f"Описание: {description}",
            reply_markup=keyboards.get_create_film_keyboard().as_markup()
        )

    @on.callback_query(F.data == 'finally_create')
    async def finally_create(self, callback: CallbackQuery, state: FSMContext) -> None:
        user_data = await state.get_data()
        code, title, description = (user_data.get('choosen_id', None),
                                    user_data.get('choosen_title', None),
                                    user_data.get('choosen_description', 'Отсутствует'))

        if code is None or title is None:
            await callback.message.edit_text(
                text='❗ Ошибка\nЧтобы создать фильм необходимо указать его название и код, попробуйте еще раз.',
                reply_markup=keyboards.back_button('add_film').as_markup()
            )
            return

        database.Film.create(id=code, name=title, description=description)
        await state.clear()
        await callback.message.edit_text(
            text='Фильм был успешно создан',
            reply_markup=keyboards.back_button('add_film').as_markup()
        )

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.exit())
    async def back(self, _: CallbackQuery) -> None:
        await admin_start(_)
        pass


class Writing_Title(Scene, state='title_film'):
    @on.callback_query.enter()
    async def enter(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите название фильма / сериала",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def title_writing(self, message: Message, state: FSMContext) -> None:
        await state.update_data(choosen_title=message.text)

        await message.answer(
            f"Установленное вами название: {message.text}",
        )

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.goto('new_film'))
    async def back(self, _: CallbackQuery) -> None:
        pass


class Writing_Description(Scene, state='description_film'):
    @on.callback_query.enter()
    async def enter(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите описание фильма / сериала",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def description_writing(self, message: Message, state: FSMContext) -> None:
        await state.update_data(choosen_description=message.text)

        await message.answer(
            text=f"Установленное вами описание: {message.text}"
        )

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.goto('new_film'))
    async def back(self, _: CallbackQuery) -> None:
        pass


class Writing_Id(Scene, state='writing_id'):
    @on.callback_query.enter()
    async def enter(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите код фильма / сериала",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )
    
    @on.message(F.text)
    async def id_writing(self, message: Message, state: FSMContext) -> None:
        print(1234)
        if database.Film.get_or_none(id=message.text.lower()) is None:
            await state.update_data(choosen_id=message.text.lower())

            await message.answer(
                f"Указанный вами код: {message.text.lower()}",
            )
            return

        await message.answer(
            "Сериал / Фильм с таким ID уже существует. Введите ID заново!",
        )

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.goto('new_film'))
    async def back(self, _: CallbackQuery) -> None:
        pass


class Delete_film(Scene, state='delete_film'):
    @on.callback_query.enter()
    async def delete_film(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите ID фильма который хотите удалить",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def film_delete(self, message: Message) -> None:
        film = database.Film.get_or_none(id=message.text)

        if film:
            film.delete_instance()
            await message.answer(f'Фильм с ID {message.text} был удален')
            return

        await message.answer('Данный фильм отсутствует!')

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.exit())
    async def back(self, _: CallbackQuery) -> None:
        await admin_start(_)
        pass


class Give_Permission(Scene, state='give_permission'):
    @on.callback_query.enter()
    async def give_permission(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите ID пользователя чьи права хотите изменить.",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def user_permissions(self, message: Message) -> None:
        try:
            user = await message.bot.get_chat(chat_id=message.text)
            username = user.username

            give_admin = GivePermissionCB(action="confirm", user_id=user.id, username=username).pack()
            take_admin = GivePermissionCB(action="take", user_id=user.id, username=username).pack()

            await message.answer(text=f'Выберите что хотите сделать с правами пользователя @{username}?',
                                 reply_markup=keyboards.permissions_buttons(callback_admin=give_admin, callback_take=take_admin).as_markup())
        except TelegramBadRequest:
            await message.answer(text="Пользователь которого вы указали отсутствует в боте!")

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.exit())
    async def back(self, _: CallbackQuery) -> None:
        await admin_start(_)
        pass

    @on.callback_query(GivePermissionCB.filter(F.action == "confirm"))
    async def confirm(self, callback: CallbackQuery, callback_data: GivePermissionCB):
        username, user_id = callback_data.username, callback_data.user_id

        user = database.User.get_or_none(id=user_id)

        if user:
            user.isAdmin = True
            user.save()

            await callback.message.edit_text(text=f'Пользователю @{username} были выданы права администратора')

    @on.callback_query(GivePermissionCB.filter(F.action == "take"))
    async def take(self, callback: CallbackQuery, callback_data: GivePermissionCB):
        username, user_id = callback_data.username, callback_data.user_id

        user = database.User.get_or_none(id=user_id)

        if user:
            user.isAdmin = False
            user.save()

            await callback.message.edit_text(text=f'Права пользователя @{username} были понижены до Пользователя')


class Channels_Panel(Scene, state='channels_panel'):
    @on.callback_query.enter()
    async def channels_panel(self, callback: CallbackQuery):
        raw_channels = database.Channels.select()
        channels: list = []

        for channel in raw_channels:
            channels.append(channel.id)

        txt_channels = ','.join(map(str, channels))

        await callback.message.edit_text(
            text=f"Вы вошли в панель управления каналами, выберите что хотите сделать. \n\nID всех каналов\n{txt_channels}",
            reply_markup=keyboards.channels_panel_buttons(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.exit())
    async def back(self, _: CallbackQuery) -> None:
        await admin_start(_)
        pass


class Add_Channel(Scene, state='add_channel'):
    @on.callback_query.enter()
    async def add_channel(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите ID канала который хотите добавить",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def new_channel(self, message: Message) -> None:
        database.Channels.get_or_create(id=message.text)

        await message.edit_text(text=f"Вы добавили канал с ID {message.text} в Базу данных")
        await self.wizard.exit()

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.goto('channels_panel'))
    async def back(self, _: CallbackQuery) -> None:
        pass


class Delete_Channel(Scene, state='delete_channel'):
    @on.callback_query.enter()
    async def writing_id(self, callback: CallbackQuery):
        await callback.message.edit_text(
            text="Напишите ID канала который хотите удалить",
            reply_markup=keyboards.back_button(ButtonsCB(action=Action.BACK).pack()).as_markup()
        )

    @on.message(
        F.text
    )
    async def delete_channel(self, message: Message) -> None:
        database.Channels.get_or_create(id=message.text)

        await message.edit_text(text=f"Вы удалили канал с ID {message.text} из Базы Данных")
        await self.wizard.exit()

    @on.callback_query(ButtonsCB.filter(F.action == Action.BACK), after=After.goto('channels_panel'))
    async def back(self, _: CallbackQuery) -> None:
        pass


async def admin_start(callback: CallbackQuery):
    await callback.message.edit_text(
        text=f"Привет, {callback.from_user.first_name}, ты находишься в админ панели, чем займемся сегодня?",
        reply_markup=keyboards.get_admin_keyboard().as_markup()
    )
