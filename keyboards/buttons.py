

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup


common_settings_buttons : InlineKeyboardButton = InlineKeyboardButton(text = "Общие настройки", callback_data = "common_settings")
users_settings_button : InlineKeyboardButton = InlineKeyboardButton(text = "Настройки пользователей", callback_data = "user_settings")


settings_markup : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[common_settings_buttons], [users_settings_button]])








change_hours_for_limit_button : InlineKeyboardButton = InlineKeyboardButton(text = "Период в часах", callback_data = "change_hours_limit")
messages_limit_button : InlineKeyboardButton = InlineKeyboardButton(text = "Лимит сообщений", callback_data = "change_message_limit")
message_excess_limit_button : InlineKeyboardButton = InlineKeyboardButton(text = "Сообщение", callback_data = "change_message_excess_limit")
time_message_excess_limit_seconds_button : InlineKeyboardButton = InlineKeyboardButton(text = "Время отображения", callback_data = "change_time_message_excess_limit_seconds")
button_back_to_menu : InlineKeyboardButton = InlineKeyboardButton(text = "Назад", callback_data = "back_to_menu")


common_config_markup : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[change_hours_for_limit_button, messages_limit_button],
                                                                                      [message_excess_limit_button, time_message_excess_limit_seconds_button],
                                                                                      [button_back_to_menu]])

back_to_menu_mrkp : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[button_back_to_menu]])

clear_time_user_btn : InlineKeyboardButton = InlineKeyboardButton(text = "Удалить текущее время", callback_data = "clear_current_time")

change_time_user_mrkp : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[clear_time_user_btn, button_back_to_menu]])


change_status_user_button : InlineKeyboardButton = InlineKeyboardButton(text = "Изменить статус 🔮", callback_data = "status_set")
change_time_user : InlineKeyboardButton = InlineKeyboardButton(text = "Задать время 🕧", callback_data = "set_time_user")
change_comment_btn : InlineKeyboardButton = InlineKeyboardButton(text = "Изменить комментарий 📖", callback_data = "change_comment")
delete_user_btn : InlineKeyboardButton = InlineKeyboardButton(text = "Удалить пользователя ❌", callback_data = "delete_user")

personaly_user_settings : InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard = [[change_status_user_button, change_time_user], [change_comment_btn],
                                                                                         [delete_user_btn] , [button_back_to_menu]])