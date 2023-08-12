import os

from loguru import logger
from vkbottle.bot import Bot, Message

from consts import ADMINS, MAGIC_NUMBER
from db_interface import add_new_group, get_all_ids, delete_group, id_by_course

# logger.disable('vkbottle') # Logger disable

bot = Bot(os.getenv('VKTOKEN'))


def is_admin(user_id: int):
    return user_id in ADMINS


async def broadcast(courses: list, text=None, attachment=None):
    for course in courses:
        groups = id_by_course(course)
        for group in groups:
            try:
                await bot.api.messages.send(
                    peer_id=(MAGIC_NUMBER + group[0]),
                    message=text,
                    attachment=attachment,
                    random_id=0
                )
            except Exception as exception:
                delete_group(group[0])


@bot.on.chat_message(text='Рассылка: <courses>, Текст <text>')
async def sharing_text(message: Message, courses: str, text: str):
    if not is_admin(message.from_id):
        await message.answer('Вы не можете проводить рассылки!')
        return
    await broadcast(courses.split(), text=text)


@bot.on.chat_message(text='Рассылка: <courses>, <share_type>')
async def sharing(message: Message, courses: str, share_type: str):
    if not is_admin(message.from_id):
        await message.answer('Вы не можете проводить рассылки!')
        return

    if share_type == 'Пост':
        attachment = message.get_wall_attachment()[0]
        publication = f"wall{attachment.owner_id}_{attachment.id}"
        await broadcast(courses.split(), attachment=[publication])
    elif share_type == 'Сообщение':
        if message.fwd_messages:
            await broadcast(courses.split(), text=message.fwd_messages[0].text)
        else:
            await message.answer('Ошибка: нет пересланного сообщения')
    else:
        await message.answer('Ошибка: Не верно указан тип')


@bot.on.chat_message(text='Добавить <course>')
async def test(message: Message, course: str):
    group_id = message.peer_id - MAGIC_NUMBER

    if course != 'admin':
        if course.isnumeric():
            course = int(course)
        else:
            await message.answer("Не верно введен курс!")
            return
        if course < 0 or course > 5:
            await message.answer("Такого курса не существует!")
            return

    else:
        course = -1

    groups_ids = get_all_ids()

    print(groups_ids)

    for i in groups_ids:
        if i[0] == group_id:
            await message.answer('Ваша беседа уже есть в списке')
            return

    add_new_group(group_id, course)

    await message.answer('Ваша беседа успешно добавлена')


@bot.on.chat_message(text='Помощь')
async def user_help(message: Message):
    if not is_admin(message.from_id):
        await message.answer('Никакой тебе помощи мудень')
        return
    await message.answer('Красавчик, тебе отсосать?')


bot.run_forever()
