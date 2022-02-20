from aiogram import Dispatcher

from handlers.admin_handler import list_groups, add_group, get_id_channel, delete_channel, get_all_user, get_suit_user
from handlers.user_handler import give_channels_to_user, check_subscribe, new_users, participate, participate_start
from referrals_bot import config
from states.state import AddGroups, UsersState


async def register_admin(dp: Dispatcher):
    dp.register_message_handler(list_groups, lambda message: message.from_user.id == int(config['ADMIN']['id_admin']),
                                commands=['groups'], state='*')
    dp.register_callback_query_handler(add_group,
                                       lambda query: query.from_user.id == int(
                                           config['ADMIN']['id_admin']) and query.data == 'add_group',
                                       state='*')
    dp.register_callback_query_handler(delete_channel,
                                       lambda query: query.from_user.id == int(
                                           config['ADMIN']['id_admin']) and 'delete_channel_' in query.data,
                                       state='*')
    dp.register_message_handler(get_id_channel,
                                lambda message: message.from_user.id == int(config['ADMIN']['id_admin']),
                                state=AddGroups.add_link)
    dp.register_message_handler(get_all_user,
                                lambda message: message.from_user.id == int(config['ADMIN']['id_admin']),
                                commands=['all_user'], state='*')
    dp.register_message_handler(get_suit_user,
                                lambda message: message.from_user.id == int(config['ADMIN']['id_admin']),
                                commands=['suit_user'], state='*')


async def register_users(dp: Dispatcher):
    dp.register_message_handler(new_users, commands=['start'], state=None)
    dp.register_message_handler(give_channels_to_user, commands=['start'], state=UsersState.subscribe_to_channel)
    dp.register_message_handler(give_channels_to_user, commands=['start'], state=UsersState.invite_friends)
    dp.register_message_handler(participate_start, commands=['start'], state=UsersState.full_user)
    dp.register_callback_query_handler(check_subscribe,
                                       lambda query: query.data == 'confirm_subscribe',
                                       state=UsersState.subscribe_to_channel)
    dp.register_callback_query_handler(participate,
                                       lambda query: query.data == 'participate',
                                       state=UsersState.full_user)
