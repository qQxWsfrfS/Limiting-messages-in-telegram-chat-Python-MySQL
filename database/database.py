
from botAttr import BotConfig



from logging import StreamHandler

import logging
import aiomysql

import sys


logger = logging.getLogger("databaseLogger")

handler = StreamHandler(stream= sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class DatabaseObject(BotConfig):


    def __init__(self):
        super().__init__()

        self._host = self._BotConfig__config["mySqlHost"] if self._BotConfig__config["mySqlHost"] else None
        self._port = self._BotConfig__config["mySqlPort"] if self._BotConfig__config["mySqlPort"] else None
        self._user = self._BotConfig__config["mySqlUser"] if self._BotConfig__config["mySqlUser"] else None
        self._password = self._BotConfig__config["mySqlPassword"] if self._BotConfig__config["mySqlPassword"] else None
        self._database = self._BotConfig__config["mySqlDatabase"] if self._BotConfig__config["mySqlDatabase"] else None
        datasObject = [self._host, self._port, self._database, self._user, self._password]




        if None in datasObject:
            logger.warning(self._BotConfig__messages["errorMessageNoneDatabaseAttribut"])


        self.connection = aiomysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db = self._database
        )
        print(self.connection)



    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def database(self):
        return self._database











    @property
    def startDatabaseInfo(self) -> str:
        readyText = f"""DATABASE MYSQL CONNECT WITH:
------------------------------------------
HOST: {self._host}
PORT: {self._port}
DATABASE: {self._database} 
USERNAME: {self._user}
PASSWORD: {"*"*len(str(self._password))}"""

        return readyText




    async def createTables(self):

        conn = await self.connection
        try:
            async with conn.cursor() as cursor:
               await cursor.execute("SHOW DATABASES;")
               response = cursor.fetchall()
               logger.info(response)
        except Exception as ex:
            print(ex)






