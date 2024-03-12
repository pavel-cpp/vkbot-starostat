from vkbottle.bot import BotLabeler
from vkbottle.user import Message

from app.bot import messages
from app.db import add_group, change_group_course, get_course_by_group_id
from app.utils import get_group_id, group_is_added, handle_course

admin_labeler = BotLabeler()
admin_labeler.vbml_ignore_case = True


@admin_labeler.message(text="Изменить курс <course>")
async def change_course(message: Message, course: str) -> None:
    if not await handle_course(message, course, check=True):
        return

    group_id = get_group_id(message)
    if not await group_is_added(group_id):
        await message.answer("Вашей беседы ещё нет в списке")
        return

    if int(course) == await get_course_by_group_id(group_id):
        await message.answer("Группе уже присвоен %s курс" % course)
        return

    await change_group_course(group_id, int(course))

    await message.answer(messages.EDITED_SUCCESSFULLY % {"course": course})


@admin_labeler.message(text="Добавить <course>")
async def add(message: Message, course: str) -> None:
    if not await handle_course(message, course):
        return

    group_id = get_group_id(message)
    if await group_is_added(group_id):
        await message.answer("Ваша беседа уже есть в списке")
        return

    await add_group(group_id, int(course))

    await message.answer(messages.ADDED_SUCCESSFULLY % {"course": course})
    await message.answer(messages.WELCOME % {"course": course})
