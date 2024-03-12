from fastapi import APIRouter, BackgroundTasks, Response

import settings
from app.bot import admin_labeler, broadcast_labeler, common_labeler
from app.schema import Data
from app.vk import bot

app = APIRouter(prefix="/api", tags=["API"])


bot.labeler.load(admin_labeler)
bot.labeler.load(common_labeler)
bot.labeler.load(broadcast_labeler)


@app.post("/callback")
async def callback(data: Data, background_tasks: BackgroundTasks) -> Response:
    if data.type == "confirmation" and data.group_id == int(settings.GROUP_ID):
        return Response(
            media_type="text/plain", content=settings.CONFIRMATION_TOKEN
        )
    background_tasks.add_task(bot.process_event, data.dict())
    return Response(media_type="text/plain", content="ok")
