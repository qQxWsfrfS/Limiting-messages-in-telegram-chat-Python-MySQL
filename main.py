

from database.database import DatabaseObject
from botAttr import BotConfig
from utils.filters import startMessage, groupByHandler


from aiogram import Bot, Dispatcher
from aiogram.types import Message




from logging import StreamHandler
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt = '[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


botCfg : BotConfig = BotConfig()
db: DatabaseObject = DatabaseObject()

botToken = None

try:
    botToken = botCfg.botToken
except TypeError as ex:
    logger.exception(f"Отсутствует ключ bot_token в файле cfg.yml: _{ex}")
    sys.exit(1)


bot : Bot =  Bot(token=botToken)
dp : Dispatcher = Dispatcher()



@dp.message(startMessage)
async def startMessageHandler(message : Message) -> None:
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")

        else:
            await bot.send_message(chat_id = message.chat.id, text = f"Добрый день {message.chat.username}")

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [startMessageHandler]. Ошибка: _{ex}")



@dp.message(groupByHandler)
async def groupByHandler(message : Message) -> None:
    try:
        #Сообщение из чата
        userInfoDict, consoleStreamText = await BotConfig.getInfoAboutUser(message.text, **dict(message.from_user))

        if botCfg.messageConsoleStream:
            logger.info(consoleStreamText)



    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [groupByHandler]. Ошибка: _{ex}")





@dp.message()
async def getTestMessage(message : Message) -> None:
    try:

        logger.info(message.json(indent = 4, exclude_none=True))
    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [getTestMessage]. Ошибка: _{ex}")










def main():
    logger.info("Бот запущен")
    logger.info(db.startDatabaseInfo)

    asyncio.run(db.createTables())

    dp.run_polling(bot, skip_updates = True)

if __name__ == "__main__":
    main()
