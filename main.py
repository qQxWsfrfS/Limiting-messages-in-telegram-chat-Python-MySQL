

from database.database import DatabaseObject
from botAttr import BotConfig, ADMIN_CONFIG
from utils.filters import startMessage, groupByHandler
from keyboards.buttons import settings_markup, common_config_markup, back_to_menu_mrkp, personaly_user_settings
from fStateMachine.fillStateMachine import FsmFillState

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.text import Text
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state



from logging import StreamHandler
import asyncio
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(logging.Formatter(fmt = '[%(asctime)s: %(levelname)s] %(message)s'))
logger.addHandler(handler)


MAX_USERS_ON_PAGE = 20

botCfg : BotConfig = BotConfig()
db: DatabaseObject = DatabaseObject()
groupById = botCfg.groupId
botToken = None

try:
    botToken = botCfg.botToken
except TypeError as ex:
    logger.exception(f"Отсутствует ключ bot_token в файле cfg.yml: _{ex}")
    sys.exit(1)


bot : Bot =  Bot(token=botToken, parse_mode="HTML")
dp : Dispatcher = Dispatcher()



@dp.message(startMessage)
async def startMessageHandler(message : Message) -> None:
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")

        else:
            await bot.send_message(chat_id = message.chat.id, text = f"Добрый день {message.chat.username}", reply_markup=settings_markup)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [startMessageHandler]. Ошибка: _{ex}")



@dp.message(groupByHandler)
async def groupByHandler(message : Message) -> None:
    try:
        #Сообщение из чата
        userInfoDict, consoleStreamText = await BotConfig.getInfoAboutUser(message.text, **dict(message.from_user))

        logger.info(userInfoDict)
        user_telegram_id = userInfoDict.get("telegramId")


        if botCfg.messageConsoleStream:
            logger.info(consoleStreamText)

        permission = await db.addUserMessage(user_telegram_id)

        if permission == "NOTPERMISSION":
            message_for_delete = await message.answer(f"Здравствуй {message.from_user.username}!\n\n{BotConfig.message_excess_limit}")
            await message.delete()
            await asyncio.sleep(BotConfig.time_message_excess_limit_seconds)
            await bot.delete_message(chat_id = groupById, message_id=message_for_delete.message_id )





    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [groupByHandler]. Ошибка: _{ex}")




#Общие настройки
@dp.callback_query(Text(text = ["common_settings"]))
async def getCommonSettings(callback : CallbackQuery):
    try:
        await callback.answer()
        await bot.delete_message(chat_id = callback.from_user.id, message_id=callback.message.message_id)

        text = f"""<b>Общие Настройки</b>
        
Период в часах: <code>{BotConfig.hours_for_limit}</code>

Доступных сообщений: <code>{BotConfig.messages_limit}</code>

Сообщение превышения лимита:  


<code>{BotConfig.message_excess_limit}</code>


Время отображения сообщения: {BotConfig.time_message_excess_limit_seconds}

<i>Укажите параметры которые хотите изменить</i>
"""

        await bot.send_message(chat_id= callback.from_user.id, text = text, reply_markup=common_config_markup)
    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [getCommonSettings]. Ошибка: {ex}")



@dp.callback_query(Text(text = ["user_settings"]))
async def getUserSettings(callback : CallbackQuery, state : FSMContext):
    try:
        text = ""
        await callback.answer()
        startSlice = 0
        endSlice = 0 + MAX_USERS_ON_PAGE



        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        users = await DatabaseObject().getAllUsers()

        await state.set_state(FsmFillState.paggination_users_state)
        await state.update_data(start = startSlice)
        await state.update_data(end = endSlice)

        button_previous : InlineKeyboardButton = InlineKeyboardButton(text = "Предыдущая", callback_data = "prev")
        button_next : InlineKeyboardButton = InlineKeyboardButton(text = "Следующая", callback_data = "next")
        button_menu : InlineKeyboardButton = InlineKeyboardButton(text = "Меню", callback_data = "back_to_menu")

        logger.info(users[endSlice: endSlice+1])
        if users[endSlice: endSlice+1] == () and startSlice == 0:
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_menu]])



        elif users[endSlice: endSlice+1] == ():
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_previous],[button_menu]])

        elif users[endSlice: endSlice+1] != () and startSlice == 0:
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_next], [button_menu]])

        else:
            paggination_mrkp : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[button_previous, button_next], [button_menu]])


        for user in users[startSlice:endSlice]:
            text += await BotConfig.readyText(user, list_mode=True)

        await bot.send_message(chat_id = callback.from_user.id, text = text, reply_markup=paggination_mrkp)



    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [getUserSettings]. Ошибка: {ex}")





@dp.callback_query(Text(text = ["prev", "next"]))
async def pagginationUsers(callback : CallbackQuery, state : FSMContext):
    try:
        await callback.answer()
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

        data = await state.get_data()
        startSlice = data.get("start")
        endSlice = data.get("end")

        text = ""

        if callback.data == "prev":
            startSlice = int(startSlice) - MAX_USERS_ON_PAGE
            endSlice = int(endSlice) - MAX_USERS_ON_PAGE

        elif callback.data == "next":
            startSlice = int(startSlice) + MAX_USERS_ON_PAGE
            endSlice = int(endSlice) + MAX_USERS_ON_PAGE

        else:
            logger.warning("error")

        await state.update_data(start=startSlice)
        await state.update_data(end=endSlice)

        users = await DatabaseObject().getAllUsers()

        button_previous: InlineKeyboardButton = InlineKeyboardButton(text="Предыдущая", callback_data="prev")
        button_next: InlineKeyboardButton = InlineKeyboardButton(text="Следующая", callback_data="next")
        button_menu: InlineKeyboardButton = InlineKeyboardButton(text="Меню", callback_data="back_to_menu")

        logger.info(users[endSlice: endSlice + 1])
        if users[endSlice: endSlice + 1] == () and startSlice == 0:
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_menu]])



        elif users[endSlice: endSlice + 1] == ():
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_previous], [button_menu]])

        elif users[endSlice: endSlice + 1] != () and startSlice == 0:
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_next], [button_menu]])

        else:
            paggination_mrkp: InlineKeyboardMarkup = InlineKeyboardMarkup(
                inline_keyboard=[[button_previous, button_next], [button_menu]])

        for user in users[startSlice:endSlice]:
            text += await BotConfig.readyText(user, list_mode=True)

        await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=paggination_mrkp)

    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [pagginationUsers]. Ошибка: {ex}")






@dp.message(StateFilter(FsmFillState.paggination_users_state))
async def getInfoAboutUser(message : Message, state : FSMContext):
    try:
        user = await DatabaseObject().getInfoAboutUser(int(message.text))
        if not user:
            await bot.send_message(chat_id=message.chat.id, text = "Пользоваель не найден")
        else:
            info = await BotConfig.readyText(user)

            await bot.send_message(chat_id=message.chat.id, text = info, reply_markup=personaly_user_settings)

            await state.set_state(default_state)
    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [getInfoAboutUser]. Ошибка: {ex}")





#Change status
@dp.callback_query(Text(text = ["status_set"]))
async def setNewStatus(callback : CallbackQuery, state : FSMContext):
    try:
        await callback.answer()
        id = int(callback.message.text.split("|")[1])



        res = await DatabaseObject().changeUserStatus(id)

        if res:
            print(res)
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            user = await DatabaseObject().getInfoAboutUser(id = id)
            info = await BotConfig.readyText(user)
            message_for_delete = await bot.send_message(chat_id = callback.from_user.id, text = "Статус обновлен")
            await asyncio.sleep(2)
            await bot.send_message(chat_id=callback.from_user.id, text = info, reply_markup=personaly_user_settings)
            await bot.delete_message(chat_id=callback.from_user.id, message_id=message_for_delete.message_id)

        else:
            await bot.send_message(chat_id=callback.from_user.id, text = "Сначала задайте время")

    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [setNewStatus]. Ошибка: {ex}")



@dp.callback_query(Text(text = ["set_time_user"]))
async def setTimeForPremium(callback : CallbackQuery, state : FSMContext):
    try:
        await callback.answer()

        id = int(callback.message.text.split("|")[1])

        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)

        await state.update_data(id_for_premium = id)
        await bot.send_message(chat_id=callback.from_user.id, text = "Укажите на сколько часов нужно дать премиум для данного пользователя", reply_markup=back_to_menu_mrkp)
        await state.set_state(FsmFillState.set_hours_time_state)
    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [setTimeForPremium]. Ошибка: {ex}")



@dp.message(StateFilter(FsmFillState.set_hours_time_state))
async def setHoursTimeForUser(message : Message, state : FSMContext):
    try:
        if not message.text.isdigit():
            await bot.send_message(chat_id=message.chat.id, text = "Укажите число", reply_markup=back_to_menu_mrkp)
        else:
            data = await state.get_data()
            id = data.get("id_for_premium")
            res = await DatabaseObject().updateTimeStartFinish(id, int(message.text))
            if res:
                await bot.send_message(chat_id=message.chat.id, text = "Данные успешно сохранены")
                await asyncio.sleep(2)
                user = await DatabaseObject().getInfoAboutUser(id=id)
                info = await BotConfig.readyText(user)
                await bot.send_message(chat_id=message.chat.id, text = info, reply_markup=personaly_user_settings)



                ##
            else:
                await  bot.send_message(chat_id=message.chat.id, text = "Не удалось сохранить изменения")
    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [setHoursTimeForUser]. Ошибка: {ex}")




@dp.callback_query(Text(text = ["change_hours_limit", "change_message_limit", "change_message_excess_limit", "change_time_message_excess_limit_seconds"]))
async def changeCommonSettings(callback : CallbackQuery, state : FSMContext):
    try:

        await callback.answer()
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)


        if callback.data == "change_hours_limit":
            await state.set_state(FsmFillState.hours_for_limit_state)

            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Укажите новый период а часах за который будет осуществляться расчет (в часах)",
                                   reply_markup=back_to_menu_mrkp)


        elif callback.data == "change_message_limit":
            await state.set_state(FsmFillState.messages_limit_state)

            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Укажите новый лимит сообщений",
                                   reply_markup=back_to_menu_mrkp)

        elif callback.data == "change_message_excess_limit":
            await state.set_state(FsmFillState.message_excess_limit_state)

            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Укажите новое сообщение в случае превышения лимита",
                                   reply_markup=back_to_menu_mrkp)

        elif callback.data == "change_time_message_excess_limit_seconds":
            await state.set_state(FsmFillState.time_message_excess_limit_seconds_state)

            await bot.send_message(chat_id=callback.from_user.id,
                                   text="Укажите время отображения сообщения в случае превышения лимита (в секундах)",
                                   reply_markup=back_to_menu_mrkp)

        else:
            logger.warning("Неизвестная ошибка в методе [changeCommonSettings]")

    except Exception as ex:
        logger.exception(f"произошла ошибка в методе [changeCommonSettings]. Ошибка: {ex}")




#Изменение периода в часах
@dp.message(StateFilter(FsmFillState.hours_for_limit_state))
async def changeHoursForLimitsState(message : Message, state : FSMContext):
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")
        else:

            if not message.text.isdigit():
                await bot.send_message(chat_id = message.chat.id, text = "Нужно указать число")
            else:
                ADMIN_CONFIG["hours_for_limit"] = int(message.text)
                await BotConfig.setNewCommonParams(**ADMIN_CONFIG)

                text = f"""<b>Общие Настройки</b>

Период в часах: <code>{BotConfig.hours_for_limit}</code>

Доступных сообщений: <code>{BotConfig.messages_limit}</code>

Сообщение превышения лимита:  


<code>{BotConfig.message_excess_limit}</code>


Время отображения сообщения: <code>{BotConfig.time_message_excess_limit_seconds}</code>


<i>Укажите параметры которые хотите изменить</i>
                """

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=common_config_markup)
                await state.set_state(default_state)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [changeHoursForLimitsState]. Ошибка: _{ex}")



#изменения сообщения
@dp.message(StateFilter(FsmFillState.message_excess_limit_state))
async def changeMessageExcessLimit(message : Message, state : FSMContext):
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")
        else:

            ADMIN_CONFIG["message_excess_limit"] = message.text
            await BotConfig.setNewCommonParams(**ADMIN_CONFIG)

            text = f"""<b>Общие Настройки</b>

Период в часах: <code>{BotConfig.hours_for_limit}</code>

Доступных сообщений: <code>{BotConfig.messages_limit}</code>

Сообщение превышения лимита:  


<code>{BotConfig.message_excess_limit}</code>


Время отображения сообщения: <code>{BotConfig.time_message_excess_limit_seconds}</code>


<i>Укажите параметры которые хотите изменить</i>
                """

            await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=common_config_markup)
            await state.set_state(default_state)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [changeMessageExcessLimit]. Ошибка: _{ex}")






@dp.message(StateFilter(FsmFillState.messages_limit_state))
async def changeMessagesLimit(message : Message, state : FSMContext):
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")
        else:

            if not message.text.isdigit():
                await bot.send_message(chat_id = message.chat.id, text = "Нужно указать число")
            else:
                ADMIN_CONFIG["messages_limit"] = int(message.text)
                await BotConfig.setNewCommonParams(**ADMIN_CONFIG)

                text = f"""<b>Общие Настройки</b>

Период в часах: <code>{BotConfig.hours_for_limit}</code>

Доступных сообщений: <code>{BotConfig.messages_limit}</code>

Сообщение превышения лимита:  


<code>{BotConfig.message_excess_limit}</code>


Время отображения сообщения: <code>{BotConfig.time_message_excess_limit_seconds}</code>


<i>Укажите параметры которые хотите изменить</i>
                """

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=common_config_markup)
                await state.set_state(default_state)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [changeMessagesLimit]. Ошибка: _{ex}")




@dp.message(StateFilter(FsmFillState.time_message_excess_limit_seconds_state))
async def changeTimeMessageExcessLimitSeconds(message : Message, state : FSMContext):
    try:
        if message.chat.id != botCfg.adminId:
            await bot.send_message(chat_id = message.chat.id, text = "Отказано в доступе")
        else:

            if not message.text.isdigit():
                await bot.send_message(chat_id = message.chat.id, text = "Нужно указать число")
            else:
                ADMIN_CONFIG["time_message_excess_limit_seconds"] = int(message.text)
                await BotConfig.setNewCommonParams(**ADMIN_CONFIG)

                text = f"""<b>Общие Настройки</b>

Период в часах: <code>{BotConfig.hours_for_limit}</code>

Доступных сообщений: <code>{BotConfig.messages_limit}</code>

Сообщение превышения лимита:  


<code>{BotConfig.message_excess_limit}</code>


Время отображения сообщения: <code>{BotConfig.time_message_excess_limit_seconds}</code>


<i>Укажите параметры которые хотите изменить</i>
                """

                await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=common_config_markup)
                await state.set_state(default_state)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [changeTimeMessageExcessLimitSeconds]. Ошибка: _{ex}")




@dp.callback_query(Text(text = ['back_to_menu']))
async def back_to_menu(callback : CallbackQuery, state : FSMContext):
    try:
        await callback.answer()
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=callback.from_user.id, text=f"Добрый день {callback.from_user.username}",
                               reply_markup=settings_markup)

        await state.set_state(default_state)

    except Exception as ex:
        logger.exception(f"Произошла ошибка в методе [back_to_menu]. Ошибка: _{ex}")





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
