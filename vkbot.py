import os

from fastapi import FastAPI, Request

from loguru import logger
from vkbottle.bot import Bot, Message

from consts import ADMINS, GROUP_ID_COEFFICIENT
from db_interface import add_group, groups_ids, delete_group, ids_by_course, init_database

app = FastAPI()

bot = Bot(os.getenv('VKTOKEN'))

init_database()

async def broadcast(courses: str, text=None, attachment=None):
    for course in courses:
        for group in ids_by_course(int(course)):
            try:
                await bot.api.messages.send(
                    peer_id=(GROUP_ID_COEFFICIENT + group),
                    message=text,
                    attachment=attachment,
                    random_id=0
                )
            except Exception as exception:
                logger.warning(exception)
                delete_group(group)


@bot.on.chat_message(text='Рассылка: <courses>, Текст <text>')
async def sharing_text(message: Message, courses: str, text: str):
    if message.from_id not in ADMINS:
        return
    await broadcast(courses, text=text)


@bot.on.chat_message(text='Рассылка: <courses>, Пост')
async def share_publication(message: Message, courses: str):
    if message.from_id not in ADMINS:
        return
    attachment = message.get_wall_attachment()[0]
    await broadcast(courses, attachment=[f"wall{attachment.owner_id}_{attachment.id}"])


@bot.on.chat_message(text='Рассылка: <courses>, Сообщение')
async def share_message(message: Message, courses: str):
    if message.from_id not in ADMINS:
        return

    if message.fwd_messages:
        await broadcast(courses, text=message.fwd_messages[0].text)
    else:
        await message.answer('Ошибка: нет пересланного сообщения')


@bot.on.chat_message(text='Добавить <course>')
async def test(message: Message, course: str):
    if course == 'admin':
        course = -1
    elif course.isnumeric() and 1 <= int(course) <= 5:
        course = int(course)
    else:
        await message.answer("Не верно введен курс!")
        return

    group_id = message.peer_id - GROUP_ID_COEFFICIENT

    if group_id in groups_ids():
        await message.answer('Ваша беседа уже есть в списке')
        return

    add_group(group_id, course)

    await message.answer('Ваша беседа успешно добавлена!')
    await message.answer('Сообщение для закрепа (Ждем от СММ)')


@bot.on.chat_message(text='Помощь')
async def user_help(message: Message):
    if message.from_id in ADMINS:
        await message.answer('Помощь для админов')


@app.post("/callback")
async def callback(request: Request):
    data = await request.json()
    print(data)
    answer = await bot.process_event([data])
    return answer

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
