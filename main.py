import asyncio
import logging

from aiogram import Bot, Dispatcher, F

from tools.database import init
from routers import base, scenes

from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.storage.memory import SimpleEventIsolation

from aiogram.utils.token import TokenValidationError

import json

with open('config.json', 'r', encoding='utf8') as f:
    config = json.load(f)

logging.basicConfig(level=logging.DEBUG)


def create_dispatcher():
    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
    )

    dispatcher.include_routers(base.router, scenes.router)
    scenes.router.callback_query.register(scenes.Add_Film.as_handler(), F.data == "add_film")
    scenes.router.callback_query.register(scenes.Delete_film.as_handler(), F.data == "delete_film")

    scenes.router.callback_query.register(scenes.Give_Permission.as_handler(), F.data == "give_permission")

    scenes.router.callback_query.register(scenes.Channels_Panel.as_handler(), F.data == "channels_panel")
    scenes.router.callback_query.register(scenes.Add_Channel.as_handler(), F.data == "add_channel")
    scenes.router.callback_query.register(scenes.Delete_Channel.as_handler(), F.data == "delete_channel")

    scene_registry = SceneRegistry(dispatcher)
    scene_registry.add(scenes.Add_Film,
                       scenes.Writing_Title,
                       scenes.Writing_Description,
                       scenes.Writing_Id,
                       scenes.Delete_film,
                       scenes.Give_Permission,
                       scenes.Channels_Panel,
                       scenes.Add_Channel,
                       scenes.Delete_Channel)

    return dispatcher


async def main():
    try:
        bot = Bot(token=config["token"])
        dp = create_dispatcher()

        await dp.start_polling(bot)
    except TokenValidationError:
        logging.critical("Введен невалидный токен")

if __name__ == "__main__":
    init()
    asyncio.run(main())
