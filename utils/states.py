from aiogram.fsm.state import StatesGroup, State



class States(StatesGroup):
    get_button_name = State()
    get_msg = State()
    get_inline_btn_name = State()
    get_inline_btn_url = State()
    get_new_text = State()
    get_sending_message = State()
    get_btn_name_sending_msg = State()
    get_btn_url_sending_msg = State()


class InviterStates(StatesGroup):
    get_inviter_btn_name_lim = State()
    get_inviter_btn_limit_lim = State()
    get_inviter_btn_name_rat = State()
    get_inviter_btn_limit_rat = State()
    get_new_limit = State()
    

class ChannelStates(StatesGroup):
    get_channel_id = State()
    get_channel_name = State()
    get_channel_type = State()
    get_editing_name = State()
