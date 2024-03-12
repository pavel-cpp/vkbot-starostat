import pytest

from app.bot import messages
from app.bot.common import user_help
from app.vk import bot


@pytest.mark.asyncio
async def test_user_help_successful(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 1
    mocker.patch("app.bot.common.settings.ADMINS", [1])

    mocker.patch.object(bot, "api", autospec=True)

    result = await user_help(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.HELP)


@pytest.mark.asyncio
async def test_user_help_not_admin(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 2
    mocker.patch("app.bot.common.settings.ADMINS", [1])

    mocker.patch.object(bot, "api", autospec=True)

    result = await user_help(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.FORBIDDEN)
