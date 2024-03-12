from hmac import compare_digest

import pytest
from fastapi.testclient import TestClient

import app as App
import settings
from app.db import get_course_by_group_id
from app.routes import app
from app.vk import bot


@pytest.fixture()
def data():
    return {
        "type": "message_new",
        "group_id": 0,
        "object": {
            "message": {
                "from_id": 0,
                "peer_id": 0,
                "text": "Рассылка: 123, Текст хуй",
                "date": 0,
                "id": 0,
                "out": 0,
            },
            "client_info": {},
        },
    }


def test_callback_confirmation(mocker, data):
    client = TestClient(app)
    test_token = "123"  # nosec
    test_group_id = "123"
    data = {
        "type": "confirmation",
        "group_id": int(test_group_id),
    }

    mocker.patch("app.routes.settings.CONFIRMATION_TOKEN", test_token)
    mocker.patch("app.routes.settings.GROUP_ID", test_group_id)

    response = client.post("/api/callback", json=data)
    assert response.status_code == 200
    assert compare_digest(response.text, test_token)


@pytest.mark.asyncio
async def test_callback_event(mocker):
    client = TestClient(app)
    data = {
        "type": "message_new",
        "group_id": 123,
        "object": {
            "message": {
                "from_id": 123,
                "peer_id": 123,
                "text": "Рассылка: 123 яйца",
                "date": 0,
                "id": 0,
                "out": 0,
                "attachments": [],
                "fwd_messages": [],
                "reply_message": None,
            },
            "client_info": {},
        },
    }

    mock_process_event = mocker.patch(
        "app.routes.bot.process_event", mocker.AsyncMock()
    )

    response = client.post("/api/callback", json=data)
    assert response.status_code == 200
    assert response.text == "ok"
    mock_process_event.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_callback_full_event(mocker, init_db, groups):
    client = TestClient(app)
    text = "Привет мир!"
    data = {
        "type": "message_new",
        "group_id": 0,
        "object": {
            "message": {
                "from_id": 1,
                "peer_id": 1,
                "text": f"Рассылка: 1234 {text}",
                "date": 0,
                "id": 0,
                "out": 0,
            },
            "client_info": {},
        },
    }
    mocker.patch("app.bot.broadcast.settings.ADMINS", [1])
    mocker.patch.object(bot, "api", autospec=True)

    bot.api.messages.send = mocker.AsyncMock()
    bot.api.messages.send.return_value = [1, 2, 3]

    response = client.post("/api/callback", json=data)
    assert response.status_code == 200
    assert response.text == "ok"

    bot.api.messages.send.assert_has_awaits(
        [
            *[
                mocker.call(
                    peer_id=settings.GROUP_ID_COEFFICIENT + x,
                    message=text,
                    random_id=0,
                    attachment=None,
                )
                for x in range(1, 4)
            ],
            mocker.call(
                peer_ids=[1],
                message=(
                    "Рассылка отправлена не полностью.\n\n"
                    "Курс 1: +\n"
                    "Курс 2: +\n"
                    "Курс 3: +\n"
                    "Курс 4: -"
                ),
                random_id=0,
            ),
        ]
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_group_id, new_course_value, new_course_text",
    [
        (1, 3, App.bot.messages.EDITED_SUCCESSFULLY),
        (2, 2, "Группе уже присвоен %(course)s курс"),
    ],
)
async def test_fix_course_change(
    mocker, init_db, groups, test_group_id, new_course_value, new_course_text
):
    peer_ids = test_group_id + settings.GROUP_ID_COEFFICIENT
    client = TestClient(app)
    data = {
        "type": "message_new",
        "group_id": test_group_id,
        "object": {
            "message": {
                "from_id": 1,
                "peer_id": (peer_ids),
                "text": f"Изменить курс {new_course_value}",
                "date": 0,
                "id": 0,
                "out": 0,
            },
            "client_info": {},
        },
    }
    mocker.patch("app.bot.broadcast.settings.ADMINS", [1])
    mocker.patch.object(bot, "api", autospec=True)
    bot.api.messages.send = mocker.AsyncMock()
    bot.api.messages.send.return_value = [1, 2, 3]
    response = client.post(
        "/api/callback",
        json=data,
    )

    assert response.status_code == 200
    assert response.text == "ok"
    assert new_course_value == await get_course_by_group_id(
        group_id=test_group_id
    )

    bot.api.messages.send.assert_has_awaits(
        [
            mocker.call(
                peer_ids=[peer_ids],
                message=new_course_text % {"course": new_course_value},
                random_id=0,
            )
        ]
    )
