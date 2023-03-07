import asyncio
from typing import AsyncIterator

from telegram import Bot, Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler

TOKEN: str = "TOKEN"
CHAT_ID: int = 123456


class MockMessageConsumer(AsyncIterator[str]):
    """Dummy MessageConsumer that just spits out a preset number of messages
    with a constant delay """

    def __init__(self, number_of_messages: int, delay: float = 1):
        self._number_of_messages = number_of_messages
        self._sent_messages = 0
        self._delay = delay

    async def __anext__(self) -> str:
        self._sent_messages += 1
        if self._sent_messages > self._number_of_messages:
            raise StopAsyncIteration

        await asyncio.sleep(self._delay)
        return f"Message {self._sent_messages}"


async def run(bot: Bot, message_consumer: MockMessageConsumer) -> None:
    async for message in message_consumer:
        await bot.send_message(chat_id=CHAT_ID, text=message)


async def start_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello, I'm a bot!", quote=True)


async def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    message_processing_loop = MockMessageConsumer(
        number_of_messages=10, delay=1.5)
    long_running_task = asyncio.create_task(
        run(application.bot, message_processing_loop))

    # Wait for all messages being sent
    await long_running_task

    # shut down the application once all messages are sent note that in this
    # simple example, we have no special logic to keep the script running
    # until the user tells it to shut down - we just shut down after all
    # messages are sent
    await application.updater.stop()
    await application.stop()
    await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
