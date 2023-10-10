from aiogram.filters.state import StatesGroup, State


class FsmFillState(StatesGroup):
    hours_for_limit_state = State()
    messages_limit_state = State()
    message_excess_limit_state = State()
    time_message_excess_limit_seconds_state = State()
    ##########
    paggination_users_state = State()
    ##########
    set_hours_time_state = State()
    #########################
    add_new_user_state = State()
    ###########################
    add_comment_state = State()
    ###########################
    user_message_state = State()


