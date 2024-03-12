import logging
import re

from vkbottle.bot import BotLabeler
from vkbottle.user import Message

import settings
from app.broadcast import broadcast

logger = logging.getLogger(__name__)

broadcast_labeler = BotLabeler()
broadcast_labeler.vbml_ignore_case = True

regex = r"[Рр]ассылка: (\d+)[ ]?(.*)"


def get_results(broadcast_result):
    results = []
    for course, course_result in broadcast_result:
        course_arr = [f"Курс {course}:"]
        for group in course_result:
            if group:
                course_arr.append("+")
            else:
                course_arr.append("-")
        results.append(" ".join(course_arr))
    return "\n".join(results)


def get_text(message: Message, text: str | None) -> str | None:
    if message.fwd_messages:
        logger.info(f"Found forward message: {message.fwd_messages[0].text}")
        return "\n\n".join(
            fwd_message.text for fwd_message in message.fwd_messages
        )
    if message.reply_message:
        logger.info(f"Found reply message: {message.reply_message.text}")
        return str(message.reply_message.text)
    logger.info("Did not found forward message")
    return text


def get_attachments(message: Message) -> str | None:
    attachments = message.get_wall_attachment()
    if attachments:
        logger.info(f"Found attachments: {attachments[0]}")
        return f"wall{attachments[0].owner_id}_{attachments[0].id}"
    return None


def parse_text(message: Message) -> tuple[str, str | None]:
    res = re.match(regex, message.text)
    if not res:
        raise ValueError("Wrong regex text")
    (courses, text) = res.groups()
    return courses, text


@broadcast_labeler.message(regex=regex)
async def sharing_text(message: Message) -> None:
    if message.from_id not in settings.ADMINS:
        return

    courses, text = parse_text(message)

    _text = get_text(message, text)
    _attachment = get_attachments(message)

    if not _text and not _attachment:
        await message.answer("Нечего пересылать")
        return

    broadcast_result = await broadcast(
        courses,
        text=_text,
        attachment=[_attachment] if _attachment else None,
    )

    if "+" in get_results(broadcast_result) and "-" not in get_results(
        broadcast_result
    ):
        text_answer = "Рассылка успешно отправлена!"
    elif "+" in get_results(broadcast_result):
        text_answer = "Рассылка отправлена не полностью."
    else:
        text_answer = "Не удалось отправить рассылку."

    await message.answer(f"{text_answer}\n\n{get_results(broadcast_result)}")
