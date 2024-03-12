from pydantic import BaseModel


class Message(BaseModel):
    from_id: int
    peer_id: int
    text: str
    date: int | None
    id: int | None
    out: int | None
    attachments: list[dict] = []
    fwd_messages: list[dict] = []
    reply_message: dict | None = None


class MessageObject(BaseModel):
    message: Message
    client_info: dict | None


class Data(BaseModel):
    type: str = "message_new"
    group_id: int
    object: MessageObject | None
