import json
from pprint import pprint
import os

from vkbottle.bot import Message
from vkbottle import Bot, API
from vkbottle import Text, BaseStateGroup
import sqlite3

from consts import admins

bot = Bot(os.getenv('VKTOKEN'))
api = bot.api

database = sqlite3.connect("database.db")

db_cursor = database.cursor()

db_cursor.execute('CREATE TABLE IF NOT EXISTS student_groups (id INT, course INT, members_count INT)')

database.commit()

@bot.on.chat_message(text='Рассылка: <type_of_message>')
async def sharing(message: Message, type_of_message: str):
    if message.from_id not in admins:
        await message.answer('Ваш id {' + str(message.from_id) + '} не является администратором')
        return
    message.answer(message.group_id)
    if type_of_message == 'Пост':
        attachments = message.get_wall_attachment()
        post_id = attachments[0].id
        owner_id = attachments[0].owner_id
        forward_txt = f"wall{owner_id}_{post_id}"
        await message.answer(attachment=[forward_txt])
    elif type_of_message == 'Сообщение':
        if message.fwd_messages:
            await message.answer(message.fwd_messages[0].text)
        else:
            await message.answer('Ошибка: нет пересланного сообщения')
    else:
        await message.answer('Ошибка: Не верно указан тип')

@bot.on.chat_message(text='Текст: <text>')
async def sharing_text(message: Message, text: str):
    if message.from_id not in admins:
        await message.answer('Ваш id {' + str(message.from_id) + '} не является администратором')
        return
    message.answer(message.group_id)
    message.answer(text)

@bot.on.chat_message(text='Добавить <course>')
async def test(message: Message, course):
    group_id = message.peer_id - int(2e9)
    members_cnt = (await api.messages.get_conversation_members(peer_id=(message.peer_id - int(2e9)))).count

    course_ids = list(db_cursor.execute(f"SELECT id FROM student_groups"))

    pprint(course_ids)

    if course != 'admin':
        if int(course) < 0 or int(course) > 5:
            await message.answer("Такого курса не существует!")
    else:
        course = '-1'

    pprint(f"INSERT INTO student_groups VALUES ({group_id}, {course}, {members_cnt})")

    for i in course_ids:
        if i[0] == group_id:
            await message.answer('Ваша беседа уже есть в списке')
            return

    db_cursor.execute(f"INSERT INTO student_groups VALUES ({group_id}, {course}, {members_cnt})")
    database.commit()
    await message.answer('Ваша беседа успешно добавлена')

    # db_cursor.execute('INSERT INTO first_course (id, peoples, name, status) VALUES (0, 2, "name", "ok")')
    # database.commit()


bot.run_forever()