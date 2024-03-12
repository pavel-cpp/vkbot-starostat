import pytest
from pytest_lazy_fixtures import lf
from vkbottle.user import Message

from app.bot.broadcast import sharing_text


@pytest.fixture()
def attachment(mocker):
    attach = mocker.Mock()
    attach.owner_id = 1
    attach.id = 1
    return attach


@pytest.fixture()
def message_simple(mocker, attachment):
    msg = mocker.Mock()
    msg.answer = mocker.AsyncMock(return_value=1)
    msg.from_id = 1
    msg.get_wall_attachment.return_value = [attachment]
    msg.fwd_messages = []
    msg.reply_message = None
    msg.text = "рассылка: 123 text"
    return msg


@pytest.fixture()
def message_with_reply(mocker, message_simple):
    reply = mocker.Mock()
    reply.text = "text"
    message_simple.reply_message = reply
    return message_simple


@pytest.fixture()
def message_with_fwd(mocker, message_simple):
    reply = mocker.Mock()
    reply.text = "text"
    message_simple.fwd_messages = [reply]
    return message_simple


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    (
        lf("message_simple"),
        lf("message_with_reply"),
        lf("message_with_fwd"),
    ),
)
@pytest.mark.parametrize(
    "broadcast_result, expected_result",
    [
        (
            (
                (
                    1,
                    (True,),
                ),
                (
                    2,
                    (True,),
                ),
                (
                    3,
                    (True,),
                ),
            ),
            "Рассылка успешно отправлена!\n\n"
            "Курс 1: +\n"
            "Курс 2: +\n"
            "Курс 3: +",
        ),
        (
            (
                (
                    1,
                    (False,),
                ),
                (
                    2,
                    (False,),
                ),
                (
                    3,
                    (False,),
                ),
            ),
            "Не удалось отправить рассылку.\n\n"
            "Курс 1: -\n"
            "Курс 2: -\n"
            "Курс 3: -",
        ),
        (
            (
                (
                    1,
                    (False,),
                ),
                (
                    2,
                    (True,),
                ),
                (
                    3,
                    (True,),
                ),
            ),
            "Рассылка отправлена не полностью.\n\n"
            "Курс 1: -\n"
            "Курс 2: +\n"
            "Курс 3: +",
        ),
    ],
)
async def test_sharing_text(
    message: Message,
    broadcast_result: tuple[tuple[int, tuple[bool]]],
    expected_result: str,
    mocker,
):
    mocker.patch("app.bot.broadcast.settings.ADMINS", [1])
    broadcast_mock = mocker.patch(
        "app.bot.broadcast.broadcast",
        new_callable=mocker.AsyncMock,
        return_value=broadcast_result,
    )

    await sharing_text(message)

    message.answer.assert_called_with(expected_result)
    broadcast_mock.assert_called_with(
        "123", text="text", attachment=["wall1_1"]
    )

    message.answer.assert_awaited()
    broadcast_mock.assert_awaited()


@pytest.mark.asyncio
async def test_sharing_text_forbidden(mocker):
    message = mocker.Mock()
    message.answer = mocker.AsyncMock()
    message.text = "рассылка: 1 text"
    message.answer.return_value = 1
    message.from_id = 2
    mocker.patch("app.bot.broadcast.settings.ADMINS", [1])

    result = await sharing_text(message)
    assert result is None
