import os

from loguru import logger
from vkbottle.bot import Bot, Message

from consts import ADMINS, ID_COEFFICIENT
from db_interface import add_new_group, get_all_ids, delete_group, id_by_course, init_database

logger.disable('vkbottle')

bot = Bot(os.getenv('VKTOKEN'))

init_database()


def is_admin(user_id: int):
    return user_id in ADMINS


async def broadcast(courses: list, text=None, attachment=None):
    for course in courses:
        groups = id_by_course(course)
        for group in groups:
            try:
                await bot.api.messages.send(
                    peer_id=(ID_COEFFICIENT + group[0]),
                    message=text,
                    attachment=attachment,
                    random_id=0
                )
            except Exception:
                delete_group(group[0])


@bot.on.chat_message(text='Рассылка: <courses>, Текст <text>')
async def sharing_text(message: Message, courses: str, text: str):
    if not is_admin(message.from_id):
        await message.answer('Вы не можете проводить рассылки!')
        return
    await broadcast(courses.split(), text=text)


@bot.on.chat_message(text='Рассылка: <courses>, Пост')
async def share_publication(message: Message, courses: str):
    if not is_admin(message.from_id):
        await message.answer('Вы не можете проводить рассылки!')
        return

    publication = f"wall{message.get_wall_attachment()[0].owner_id}_{message.get_wall_attachment()[0].id}"
    await broadcast(courses.split(), attachment=[publication])


@bot.on.chat_message(text='Рассылка: <courses>, Сообщение')
async def share_message(message: Message, courses: str):
    if not is_admin(message.from_id):
        await message.answer('Вы не можете проводить рассылки!')
        return

    if message.fwd_messages:
        await broadcast(courses.split(), text=message.fwd_messages[0].text)
    else:
        await message.answer('Ошибка: нет пересланного сообщения')

@bot.on.chat_message(text='Рассылка: <courses>, ')
async def incorrect_message(message: Message, courses: str):
    if is_admin(message.from_id):
        await message.answer('Не верно введена команда')
        return
    await message.answer('Вы не можете проводить рассылки!')

@bot.on.chat_message(text='Добавить <course>')
async def test(message: Message, course: str):

    if course != 'admin':
        if course.isnumeric() and (1 <= int(course) <= 5):
            course = int(course)
        else:
            await message.answer("Не верно введен курс!")
            return
    else:
        course = -1

    groups_ids = get_all_ids()
    group_id = message.peer_id - ID_COEFFICIENT

    for id in groups_ids:
        if id[0] == group_id:
            await message.answer('Ваша беседа уже есть в списке')
            return

    add_new_group(group_id, course)

    await message.answer('Ваша беседа успешно добавлена')
    await message.answer('Сообщение для закрепа (Ждем от СММ)')


@bot.on.chat_message(text='Помощь')
async def user_help(message: Message):
    if is_admin(message.from_id):
        await message.answer('Помощь для админов')


bot.run_forever()
