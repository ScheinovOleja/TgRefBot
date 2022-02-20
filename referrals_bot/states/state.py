from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    start_register = State()
    in_registered = State()


class AddGroups(StatesGroup):
    add_link = State()


class UsersState(StatesGroup):
    subscribe_to_channel = State()
    invite_friends = State()
    full_user = State()
