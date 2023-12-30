from aiogram.filters import BaseFilter
from aiogram.types import Message

from tools.database import *


class ItsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = User.get_or_none(id=message.from_user.id)

        if user.isAdmin:
            return True

        return False