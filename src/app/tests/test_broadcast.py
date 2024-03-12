from unittest.mock import AsyncMock

import pytest
from vkbottle import VKAPIError
from vkbottle.exception_factory.code_exception import CodeExceptionMeta

import settings
from app.broadcast import broadcast, course_broadcast, group_broadcast
from app.exceptions import DBError
from app.vk import bot


class VKAPIErrorPermissionDenied(  # type: ignore[call-arg]
    VKAPIError,
    code=7,
    metaclass=CodeExceptionMeta,
):
    ...


class VKAPICommonError(  # type: ignore[call-arg]
    VKAPIError,
    code=1,
    metaclass=CodeExceptionMeta,
):
    ...


@pytest.mark.asyncio
async def test_group_broadcast_successful(mocker):
    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    bot.api.messages.send = AsyncMock()
    bot.api.messages.send.return_value = 1

    result = await group_broadcast(group, text, attachment)
    assert result == 1
    bot.api.messages.send.assert_awaited()
    bot.api.messages.send.assert_called_with(
        peer_id=(settings.GROUP_ID_COEFFICIENT + group),
        message=text,
        attachment=attachment,
        random_id=0,
    )


@pytest.mark.asyncio
async def test_group_broadcast_permissions_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.warning")

    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    error = VKAPIErrorPermissionDenied(
        error_msg="Permission to perform this action is denied by user"
    )
    bot.api.messages.send = AsyncMock(side_effect=error)

    delete_group_mock = mocker.patch(
        "app.broadcast.delete_group", new_callable=AsyncMock
    )

    result = await group_broadcast(group, text, attachment)

    assert not result
    bot.api.messages.send.assert_awaited()
    delete_group_mock.assert_awaited()
    delete_group_mock.assert_called_once_with(group)
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_group_broadcast_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.error")

    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    error = VKAPICommonError(error_msg="Error")
    bot.api.messages.send = AsyncMock(side_effect=error)

    result = await group_broadcast(group, text, attachment)

    assert not result
    bot.api.messages.send.assert_awaited()
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_course_broadcast_empty(mocker):
    course = 2023
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    get_group_ids_by_course_mock = mocker.patch(
        "app.broadcast.get_group_ids_by_course", new_callable=AsyncMock
    )
    get_group_ids_by_course_mock.return_value = []

    result = await course_broadcast(course, text, attachment)

    assert result == (course, (False,))
    get_group_ids_by_course_mock.assert_awaited()
    get_group_ids_by_course_mock.assert_called_once_with(course)


@pytest.mark.asyncio
async def test_course_broadcast_exception(mocker):
    log_mock = mocker.patch("app.broadcast.logger.error")

    course = 2023
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    error = DBError("Error")
    mocker.patch(
        "app.broadcast.get_group_ids_by_course", new_callable=AsyncMock
    ).side_effect = error

    result = await course_broadcast(course, text, attachment)

    assert result == (course, (False,))
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_course_broadcast_successful(mocker):
    course = 2023
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    get_group_ids_by_course_mock = mocker.patch(
        "app.broadcast.get_group_ids_by_course", new_callable=AsyncMock
    )
    get_group_ids_by_course_mock.return_value = [1, 2, 3]

    group_broadcast_mock = mocker.patch(
        "app.broadcast.group_broadcast", new_callable=AsyncMock
    )
    group_broadcast_mock.return_value = True

    result = await course_broadcast(course, text, attachment)

    assert result == (course, (True,) * 3)
    get_group_ids_by_course_mock.assert_awaited()
    get_group_ids_by_course_mock.assert_called_once_with(course)
    group_broadcast_mock.assert_awaited()
    group_broadcast_mock.assert_has_awaits(
        [
            mocker.call(1, text, attachment),
            mocker.call(2, text, attachment),
            mocker.call(3, text, attachment),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_empty(mocker):
    courses = "2023"
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    course_broadcast_mock = mocker.patch(
        "app.broadcast.course_broadcast", new_callable=AsyncMock
    )
    course_broadcast_mock.return_value = (False,)

    result = await broadcast(courses, text, attachment)

    assert result == ((False,),) * 3
    course_broadcast_mock.assert_awaited()
    course_broadcast_mock.assert_has_awaits(
        [
            mocker.call(0, text, attachment),
            mocker.call(2, text, attachment),
            mocker.call(3, text, attachment),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_successful(mocker):
    courses = "2023"
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    course_broadcast_mock = mocker.patch(
        "app.broadcast.course_broadcast", new_callable=AsyncMock
    )
    course_broadcast_mock.return_value = (True,)

    result = await broadcast(courses, text, attachment)

    assert result == ((True,),) * 3
    course_broadcast_mock.assert_awaited()
    course_broadcast_mock.assert_has_awaits(
        [
            mocker.call(0, text, attachment),
            mocker.call(2, text, attachment),
            mocker.call(3, text, attachment),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_not_numeric_error(mocker):
    courses = "qwe"
    text = "hello world!"
    attachment = ["123"]

    log_mock = mocker.patch("app.broadcast.logger.error")
    result = await broadcast(courses, text, attachment)
    assert not result
    log_mock.assert_called_with("Courses is not numeric")
