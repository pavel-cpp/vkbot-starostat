from pprint import pprint
import os

from vkbottle.bot import Bot, Message
import sqlite3

from consts import admins

bot = Bot(os.getenv('VKTOKEN'))

database = sqlite3.connect("database.db")

db_cursor = database.cursor()

db_cursor.execute('CREATE TABLE IF NOT EXISTS student_groups (id INT, course INT, members_count INT)')

database.commit()


async def share_messages(courses: list, text=None, attachment=None):
    for course in courses:
        groups = list(db_cursor.execute(f"SELECT id FROM student_groups WHERE course == {course}"))
        for group in groups:
            await bot.api.messages.send(
                peer_id=(int(2e9) + group[0]),
                message=text,
                attachment=attachment,
                random_id=0
            )


@bot.on.chat_message(text='Рассылка: <courses>, <share_type>')
async def sharing(message: Message, courses: str, share_type: str):
    if message.from_id not in admins:
        await message.answer('Ваш id {' + str(message.from_id) + '} не является администратором')
        return

    courses_list = courses.split()

    if share_type == 'Пост':
        attachment = message.get_wall_attachment()[0]
        forward_txt = f"wall{attachment.owner_id}_{attachment.id}"
        await share_messages(courses_list, attachment=[forward_txt])
    elif share_type == 'Сообщение':
        if message.fwd_messages:
            await share_messages(courses_list, text=message.fwd_messages[0].text)
        else:
            await message.answer('Ошибка: нет пересланного сообщения')
    else:
        await message.answer('Ошибка: Не верно указан тип')


@bot.on.chat_message(text='Рассылка: <courses>, Текст <text>')
async def sharing_text(message: Message, text: str):
    return
@bot.on.chat_message(text='Добавить <course>')
async def test(message: Message, course):
    group_id = message.peer_id - int(2e9)
    members_cnt = (await bot.api.messages.get_conversation_members(peer_id=(message.peer_id - int(2e9)))).count

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

@bot.on.chat_message()
async def sharing_text(message: Message):
    await message.answer('Неизвестная команда')

bot.run_forever()
