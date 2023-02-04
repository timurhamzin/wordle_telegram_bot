import logging
import time

import telegram


async def start(
        update: telegram.Update,
        context: telegram.ext.ContextTypes.DEFAULT_TYPE):
    global CHAT_ID, BOT
    CHAT_ID = update.effective_chat.id
    BOT = context.bot
    await BOT.send_message(
        chat_id=CHAT_ID,
        text=f'Go about you day, {update.message.chat.first_name}. '
             'You will get notified once your homework status changes.'
    )


async def send_message(message: str) -> None:
    from check_homework_status_bot import check_started
    check_started()
    await BOT.send_message(chat_id=CHAT_ID, text=message)
    logging.info(f'A message was sent at timestamp {int(time.time())}')