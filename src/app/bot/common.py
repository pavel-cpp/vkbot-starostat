from vkbottle.bot import BotLabeler
from vkbottle.user import Message
from vkbottle_types.objects import MessagesSendUserIdsResponseItem

import settings
from app.bot import messages

common_labeler = BotLabeler()
common_labeler.vbml_ignore_case = True


@common_labeler.message(text="Помощь")
async def user_help(message: Message) -> MessagesSendUserIdsResponseItem:
    if message.from_id not in settings.ADMINS:
        return await message.answer(messages.FORBIDDEN)

    return await message.answer(messages.HELP)
