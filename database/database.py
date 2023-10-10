
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

        columns = ("id", "time", "user_id")
        time_difference_secconds = int((datetime.datetime.now() - userMessages[-1 * int(BotConfig.messages_limit)][1]).total_seconds())
        permission_seconds = int(BotConfig.hours_for_limit) * 60 * 60


        if (time_difference_secconds > permission_seconds):

            return True
            #можно комментировать
        else:

            return False



    async def addUserMessage(self, telegram_id : int) -> None:
        conn = await self.connection()
        try:
            now = datetime.datetime.now()
            formatted_date_time = now.strftime(BASE_TIME_SAMPLE)



            dt_add_limit_time_hours = now + datetime.timedelta(hours = int(BotConfig.hours_for_limit))

            async with conn.cursor() as cursor:

                await cursor.execute(f'''SELECT * FROM users WHERE user_id = '{telegram_id}';''')

                response = await cursor.fetchone()


                if not response:
                    await cursor.execute(f"""SELECT * FROM message WHERE user_id = {telegram_id};""")

                    usersMessages = await cursor.fetchall()

                    countMessages = len(usersMessages)



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
                else:

                    #Пользователь есть в таблице users

                    if response[-2] == 1:


                        #await self.updateTimeStartFinish(int(response[0]))
                        await cursor.execute(
                            f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')
                        await conn.commit()
                        return

                    else:

                        #Если статус равен 0 проверяем время

                        if response[-3]!=None:

                            if response[-3] > datetime.datetime.now():
                                await cursor.execute(
                                    f'''INSERT INTO message(time, user_id) VALUES ('{formatted_date_time}', {telegram_id});''')

                                await conn.commit()
                                return
                            else:

                                #Cтатус 0 и время вышло проводим проверку

                                await cursor.execute(f"""SELECT * FROM message WHERE user_id = {telegram_id};""")

                                usersMessages = await cursor.fetchall()

                                countMessages = len(usersMessages)



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

                        else:
                            #Время не указано и статус 0

                            await cursor.execute(f"""SELECT * FROM message WHERE user_id = {telegram_id};""")

                            usersMessages = await cursor.fetchall()

                            countMessages = len(usersMessages)



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

                if response[-2] == 1:
                    await cursor.execute(f"""UPDATE users SET status = 0 WHERE id = {id};""")
                    await conn.commit()
                    return True

                else:

                    await cursor.execute(f"""UPDATE users SET status = 1 WHERE id = {id};""")
                    await conn.commit()

                    return  True


        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")


    async def updateTimeStartFinish(self, id : int, hours : int = None, **kwargs):
        conn = await self.connection()
        try:
            dt_add_limit_time_hours = None
            now = datetime.datetime.now()

            if hours is not None:
                dt_add_limit_time_hours = now + datetime.timedelta(hours=hours)

            async with conn.cursor() as cursor:
                if hours is not None:
                    await cursor.execute(f"""UPDATE users 
                                        SET time_start = '{now.strftime(BASE_TIME_SAMPLE)}', time_finish = '{dt_add_limit_time_hours.strftime(BASE_TIME_SAMPLE)}'
                                        WHERE id = {id};""")

                else:

                    telegram_id = kwargs.get("telegram_id", False)
                    if telegram_id:
                        await cursor.execute(f"""UPDATE users 
                                                                SET time_start = '{now.strftime(BASE_TIME_SAMPLE)}', time_finish = '{dt_add_limit_time_hours.strftime(BASE_TIME_SAMPLE)}'
                                                                WHERE user_id = {telegram_id};""")
                    else:

                        await cursor.execute(f"""UPDATE users 
                                        SET time_start = NULL, time_finish = NULL, status = 0
                                        WHERE id = {id};""")

                await conn.commit()
                return True

        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")


    async def addNewUserInUsers(self, telegram_id : int) -> bool:
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''INSERT INTO users(user_id, status) VALUES('{telegram_id}', 0);''')

                await conn.commit()
                return True

        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")


    async def deleteUser(self, id : int) -> bool:
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''DELETE FROM users WHERE id = {id};''')
                await conn.commit()
                return True



        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")
            return False


    async def setCommetForUser(self, id : int, comment : str) -> bool:
        conn = await self.connection()
        try:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''UPDATE users SET comment = '{comment}' WHERE id = {id};''')
                await conn.commit()
                return True

        except Exception as ex:
            logger.exception(f"Ошибка: _{ex}")
            return False









