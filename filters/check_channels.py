from datetime import timedelta, datetime

from aiogram.enums import ChatMemberStatus
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from tools.database import *
from tools.keyboards import channels_generate


class CheckChannels(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        subscribed = 0
        channels_ = []

        channels = Channels.select()

        for channel in channels:
            try:
                user_status = await message.bot.get_chat_member(chat_id=channel.id, user_id=message.from_user.id)
                link = await message.bot.create_chat_invite_link(chat_id=channel.id, name='invite', expire_date=timedelta(days=7))
                telegram_channel = await message.bot.get_chat(chat_id=channel.id)

                if user_status.status != ChatMemberStatus.LEFT:
                    subscribed += 1

                channels_.append({'invite': link.invite_link,
                                   'title': telegram_channel.title})

            except TelegramBadRequest:
                await message.answer(text="❗Упс.. \n\nПроизошла ошибка. Обратитесь к создателю бота.")
                return False

        if channels.count() == subscribed:
            return True

        await message.answer(text="❗Перед использованием бота нужно подписаться на каналы ниже!",
                             reply_markup=channels_generate(channels_).as_markup())
        return False
