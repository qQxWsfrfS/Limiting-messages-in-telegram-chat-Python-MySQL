

from pathlib import Path
from logging import StreamHandler


import aiofiles
import sys
import logging
import yaml
import time



messagesAttribut = Path("utils/messages.yml")
adminConfig = Path("utils/admin_config.yml")

logger = logging.getLogger("attributLogger")
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream= sys.stdout)
logger.addHandler(handler)


with open(adminConfig, "r", encoding="UTF-8") as file:
    ADMIN_CONFIG = yaml.safe_load(file)


class BotConfig:

    hours_for_limit = ADMIN_CONFIG["hours_for_limit"]
    messages_limit = ADMIN_CONFIG["messages_limit"]
    message_excess_limit = ADMIN_CONFIG["message_excess_limit"]
    time_message_excess_limit_seconds = ADMIN_CONFIG["time_message_excess_limit_seconds"]

    def __init__(self):

        with open(messagesAttribut, "r", encoding="UTF-8") as file:
            self.__messages = yaml.safe_load(file)

        #Объект конфигураций
        with open("cfg.yml", 'r') as file:
            self.__config = yaml.safe_load(file)


        #Токен бота заносить в cfg.yml
        try:
            self.__botToken = self.__config["bot_token"]
        except KeyError:
            logger.error("Отсутствует поле с ключем")
            sys.exit(1)

        self.__adminId = self.__config["admin_id"]
        self.__groupID = self.__config["chat_group_id"]
        self.__messageConsoleStream = self.__config["messageConsoleStream"]

        #################################




    @property
    def botToken(self) -> str:
        return self.__botToken #TypeError если удалили ключ для токена

    @property
    def adminId(self) -> str:
        return self.__adminId

    @property
    def groupId(self) -> int:
        return self.__groupID


    @property
    def messageConsoleStream(self) -> bool:
        if str(self.__messageConsoleStream).lower() == "true":
            return True
        else:
            return False



    @classmethod
    async def setNewCommonParams(cls, **kwargs):
        try:
            async with aiofiles.open(adminConfig, "w", encoding="UTF-8") as file:
                await file.write(yaml.dump(kwargs))

                BotConfig.hours_for_limit = kwargs.get("hours_for_limit")
                BotConfig.messages_limit = kwargs.get("messages_limit")
                BotConfig.message_excess_limit = kwargs.get("message_excess_limit")
                BotConfig.time_message_excess_limit_seconds = kwargs.get("time_message_excess_limit_seconds")

                logger.info("[+] Настройки обновлены")

        except Exception as ex:
            logger.exception(f"Error: _{ex}")



    @classmethod
    async def readyText(cls, list_info : tuple, **kwargs):
        try:
            list_mode = kwargs.get("list_mode", False)
            if list_mode:
                text = f"id: <code>{list_info[1]}</code> | status: <code>{list_info[4]}</code>\n"
                return text
            text = f"""
            <b>Информация о пользователе</b>
            
id:<code>{list_info[1]}</code>
start: <code>{list_info[2] if list_info[2] else "Отсутствует"}</code>
finish: <code>{list_info[3] if list_info[3] else "Отсутствует"}</code>
status : <code>{list_info[4]}</code>

|{list_info[0]}"""

            return text
        except Exception as ex:
            logger.error(f"Ошибка:_{ex}")


    @classmethod
    async def getInfoAboutUser(cls,messageText : str, **kwargs):
        textForMessage = await cls.readyMessageText(messageText, kwargs)
        userInfoDict = {}
        userInfoDict["telegramId"] = kwargs.get("id")
        userInfoDict["username"] = kwargs.get("username")

        if not cls.messageConsoleStream:
            textForMessage = None

        return userInfoDict, textForMessage




    @staticmethod
    async def readyMessageText(text : str = None, infoFortext : dict = None) -> str:
        text = f"""Сообщение от пользователя: 
id: {infoFortext.get("id")}
Бот: {"Да" if infoFortext.get("is_bot") else "Нет" }
Имя: {infoFortext.get("first_name") if infoFortext.get("first_name") else "Отсутствует"}
Фамилия: {infoFortext.get("last_name") if infoFortext.get("last_name") else "Отсутствует"}
Юзернэйм: {infoFortext.get("username") if infoFortext.get("username") else "Отсутствует"}
Код Языка: {infoFortext.get("language_code") if infoFortext.get("language_code") else "Отсутствует"}
Премиум: {infoFortext.get("is_premium") if infoFortext.get("is_premium") else "Отсутствует"}

######################
Сообщение: {text}
"""
        return text












