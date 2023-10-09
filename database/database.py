
from botAttr import BotConfig



from logging import StreamHandler
import datetime

import asyncio
import logging
import aiomysql

import sys


BASE_TIME_SAMPLE = "%Y-%m-%d %H:%M:%S"

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





    async def connection(self):
        conn = await aiomysql.connect(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            db = self._database )

        return conn

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

        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:

               await cursor.execute(f"SELECT 1 FROM information_schema.tables WHERE table_name = 'message' LIMIT 1")
               messageRes = cursor.rowcount > 0
               if messageRes:
                   logger.info("Table message exist")
               else:
                   await cursor.execute(self._BotConfig__messages["createTableMessage"])
                   logger.info("Table message created")



               await cursor.execute(self._BotConfig__messages["createTableUsers"])
               logger.info("Table users create")


            logger.info("MYSQL DATABASE IS READY")



        except Exception as ex:
            logger.error(f"Не удалось создать таблицы в базе данных. Ошибка: {ex}")


    @staticmethod
    async def getTimeDifference(userMessages : tuple) -> bool:
        print(f"type user message - {type(userMessages)}")
        columns = ("id", "time", "user_id")
        time_difference_secconds = int((datetime.datetime.now() - userMessages[-1 * int(BotConfig.messages_limit)][1]).total_seconds())
        permission_seconds = int(BotConfig.hours_for_limit) * 60 * 60

        print(f"{time_difference_secconds} + and + {permission_seconds}")
        if (time_difference_secconds > permission_seconds):
            print("Можно комментить")
            return True
            #можно комментировать
        else:
            print("нельзя комментить")
            return False



    async def addUserMessage(self, telegram_id : int) -> None:
        conn = await self.connection()
        try:
            now = datetime.datetime.now()
            formatted_date_time = now.strftime(BASE_TIME_SAMPLE)


            print(BotConfig.hours_for_limit)
            dt_add_limit_time_hours = now + datetime.timedelta(hours = int(BotConfig.hours_for_limit))
            print(dt_add_limit_time_hours)
            async with conn.cursor() as cursor:

                await cursor.execute(f'''SELECT * FROM users WHERE user_id = '{telegram_id}';''')

                response = await cursor.fetchone()
                print(f"res {response}")

                if not response:
                    await cursor.execute(
                        f'''INSERT INTO users(user_id, status) VALUES ({telegram_id} , 0)''')

                    await cursor.execute(f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')

                    await conn.commit()
                    #Новый пользователь
                else:

                    if response[-1] == 1:

                        if response[-2] > datetime.datetime.now():
                            await cursor.execute(
                                f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')

                            await conn.commit()
                            return

                        else:
                            #Премиум кончился
                            await self.updateTimeStartFinish(int(response[0]))
                            logger.info(f"У ползователя {response[1]} закончился премиум")
                            return



                    await cursor.execute(f"""SELECT * FROM message WHERE user_id = {telegram_id};""")

                    usersMessages = await cursor.fetchall()

                    countMessages = len(usersMessages)

                    print(f'user messages = {usersMessages} count = {countMessages}')

                    if countMessages <= int(BotConfig.messages_limit):
                        await cursor.execute(
                            f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')

                        await conn.commit()

                    else:
                        permissionMessage = await self.getTimeDifference(usersMessages)
                        if permissionMessage:
                            await cursor.execute(
                                f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')

                            await conn.commit()

                        else:

                            return "NOTPERMISSION"


        except Exception as ex:
            logger.error(ex)



    async def getAllUsers(self) -> tuple:
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f"""SELECT * FROM users;""")
                response = await cursor.fetchall()

                return  response
        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")



    async def getInfoAboutUser(self, telegram_id : int = None, **kwargs):
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:

                id = kwargs.get("id", False)
                if not id:
                    await cursor.execute(f"""SELECT * FROM users WHERE user_id = {telegram_id};""")
                else:
                    await cursor.execute(f"""SELECT * FROM users WHERE id = {id};""")

                response = await cursor.fetchone()
                if response is None:
                    return False

                return response
        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")


    async def changeUserStatus(self, id : int) -> bool:
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f"""SELECT * FROM users WHERE id = {id};""")

                response = await cursor.fetchone()
                print(f"info about user = {response}")
                if response[-1] == 1:
                    await cursor.execute(f"""UPDATE users SET status = 0 WHERE id = {id};""")
                    await conn.commit()
                    return True

                else:
                    if response[-2] == None or response[-2] < datetime.datetime.now():
                        return False # Если нужно задать время

                    else:
                        await cursor.execute(f"""UPDATE users SET status = 1 WHERE id = {id};""")
                        await conn.commit()

                        return  True


        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")


    async def updateTimeStartFinish(self, id : int, hours : int = None):
        conn = await self.connection()
        try:

            now = datetime.datetime.now()

            dt_add_limit_time_hours = now + datetime.timedelta(hours=hours)

            async with conn.cursor() as cursor:
                if hours is not None:
                    await cursor.execute(f"""UPDATE users 
                                        SET time_start = '{now.strftime(BASE_TIME_SAMPLE)}', time_finish = '{dt_add_limit_time_hours.strftime(BASE_TIME_SAMPLE)}'
                                        WHERE id = {id};""")

                else:
                    await cursor.execute(f"""UPDATE users 
                                    SET time_start = NULL, time_finish = NULL
                                    WHERE id = {id};""")

                await conn.commit()
                return True

        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")







