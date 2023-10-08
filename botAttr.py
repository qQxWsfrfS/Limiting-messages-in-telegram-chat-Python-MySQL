

from pathlib import Path

import sys
import logging
import yaml
import asyncio


messagesAttribut = Path("utils/messages.yml")

logger = logging.getLogger("attributLogger")
logger.setLevel(logging.DEBUG)


class BotConfig:

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












