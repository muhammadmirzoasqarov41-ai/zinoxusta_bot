from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    full_name = State()
    phone = State()
    region = State()
    district = State()
    role = State()
    profession = State()
    profession_custom = State()
    bio = State()
    photo = State()
    purpose = State()


class AdminAddDiamonds(StatesGroup):
    user_id = State()
    amount = State()


class AdminRemoveDiamonds(StatesGroup):
    user_id = State()
    amount = State()


class AdminBroadcast(StatesGroup):
    message = State()


class AdminAdBroadcast(StatesGroup):
    message = State()


class AdminSendById(StatesGroup):
    user_id = State()
    message = State()


class AdminBlockUser(StatesGroup):
    user_id = State()


class AdminUnblockUser(StatesGroup):
    user_id = State()


class AdminGiveAllDiamonds(StatesGroup):
    amount = State()


class ProfileEdit(StatesGroup):
    field = State()
    value = State()


class RateMaster(StatesGroup):
    master_id = State()
    rating = State()
    comment = State()


class SearchProfession(StatesGroup):
    profession = State()


class SearchRegion(StatesGroup):
    region = State()
