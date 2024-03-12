from vkbottle.user import Message

import settings
from app.db import get_groups_ids


def process_course(course: str | int) -> int:
    if course == "admin":
        return -1
    if isinstance(course, int):
        return course
    if isinstance(course, str) and course.isnumeric():
        return int(course)
    return 0


async def handle_course(
    message: Message, course: str | int, check: bool = False
) -> bool:
    _course = process_course(course)

    if _course not in (-1, 1, 2, 3, 4, 5):
        await message.answer("Не верно введен курс!")
        return False

    if check:
        groups_ids = await get_groups_ids()

        if not groups_ids:
            await message.answer("Произошла непредвиденная ошибка!")
            return False

    return True


def get_group_id(message: Message) -> int:
    return int(message.peer_id) - settings.GROUP_ID_COEFFICIENT


async def group_is_added(group_id: int) -> bool:
    return group_id in await get_groups_ids()
