from .main import app

broker = app.broker


@broker.task
async def message(text: str) -> None:
    print(text)


@broker.task
async def error(text: str) -> None:
    raise Exception(text)
