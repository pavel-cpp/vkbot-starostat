import json
from pprint import pprint
import os

from vkbottle.bot import Bot, Message
from vkbottle import Text, BaseStateGroup

from consts import admins

bot = Bot(os.getenv('VKTOKEN'))

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




bot.run_forever()