from sqlalchemy.orm import joinedload
from taskiq import Context, TaskiqDepends

from .main import app

broker = app.broker


@broker.task
async def message(text: str) -> None:
    print(text)


@broker.task
async def error(text: str) -> None:
    raise Exception(text)


@broker.task
async def message_sent(message_id: int, context: Context = TaskiqDepends()) -> None:
    from correspondence.models import Conversation, Message

    async with app.db.async_session_local() as asession:
        message = await Message.repository(asession).aget(
            message_id,
            options=[
                joinedload(Message.sender),
                joinedload(Message.conversation).options(
                    joinedload(Conversation.receiver),
                    joinedload(Conversation.phone_number),
                ),
            ],
        )

        if message:
            await message.send(asession, app.provider, commit=True)
