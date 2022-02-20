from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pony.orm import db_session, commit

from models import Groups, AllUsers, SubscribeUsers, InvitedUser, MembersAirdrop
from states.state import UsersState
from referrals_bot import bot, dp


async def alert_referrer_user(referrer):
    with db_session:
        count_referrers = InvitedUser.select(lambda u: u.referrals == referrer).count()
        if count_referrers >= 5:
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Participate!', callback_data='participate'))
            await bot.send_message(chat_id=referrer.tg_id,
                                   text='You invited 5 friends!\nPress button to register as participant of giveaway!',
                                   reply_markup=markup)
            MembersAirdrop(user=AllUsers.get(tg_id=str(referrer.tg_id)))
            state = dp.current_state(chat=referrer.tg_id, user=referrer.tg_id)
            await state.set_state(UsersState.full_user)


async def new_users(message: Message, state: FSMContext):
    with db_session:
        user = AllUsers.get_or_create(tg_id=str(message.from_user.id))[0]
        if " " in message.text:
            referrer_candidate = message.text.split()[1]
            referrer = AllUsers.get(tg_id=referrer_candidate)
            if referrer:
                if referrer == user:
                    await message.answer('You cannot invite yourself!')
                else:
                    who_invite = InvitedUser.select().filter(referrals=referrer, user=user)
                    if not who_invite:
                        InvitedUser(
                            user=user,
                            referrals=referrer
                        )
                        await message.answer('You have successfully subscribed via the invitation link!')
                    else:
                        await message.answer('You are already subscribed to the invitation link!')
            else:
                await message.answer('Could not find the user who invited you!')
            await alert_referrer_user(referrer)
    await state.set_state(UsersState.subscribe_to_channel)
    await give_channels_to_user(message, state)


@db_session
async def give_channels_to_user(message: Message, state: FSMContext):
    markup = InlineKeyboardMarkup()
    all_group = Groups.select()
    text = 'You were subscribed successfully. Invite 5 friends to participate in every week giveaway.' \
           'Your referral link:\n' \
           f'<code>t.me/iuyghrtougyeguyuyrtgkuyhyru_bot?start={message.chat.id}</code>'
    check = True
    for group in all_group:
        user = await bot.get_chat_member(group.id_group, message.from_user.id)
        if user.status == 'member' or user.status == 'creator':
            markup.add(InlineKeyboardButton(f'✅ {group.name_group}', url=group.link_group))
        else:
            markup.add(InlineKeyboardButton(f'❌ {group.name_group}', url=group.link_group))
            text = """Hello, you have the opportunity to participate in every week giveaway. 

Every week we giveaway some fundamental tokens through the subscribers. You have opportunity to win BTC, BNB, ETH, TRX, Polygon. To participate in giveaway, subscribe on following channels and invite at least 5 friends. 

In case of win you will receive message only through this bot! No one will write you DM.

Send join request and after approval press Approve subscription."""
            check = False
    if check:
        await message.answer(text)
        await state.set_state(UsersState.invite_friends)
    else:
        markup.add(InlineKeyboardButton('Approve subscription', callback_data='confirm_subscribe'))
        await message.answer(text, reply_markup=markup)
        await UsersState.first()


@db_session
async def check_subscribe(query: CallbackQuery, state: FSMContext):
    markup = InlineKeyboardMarkup()
    all_group = Groups.select()
    text = 'You were subscribed successfully. Invite 5 friends to participate in every week giveaway.' \
           'Your referral link:\n' \
           f'<code>t.me/iuyghrtougyeguyuyrtgkuyhyru_bot?start={query.message.chat.id}</code>'
    check = True
    for group in all_group:
        user = await bot.get_chat_member(group.id_group, query.from_user.id)
        if user.status == 'member' or user.status == 'creator':
            markup.add(InlineKeyboardButton(f'✅ {group.name_group}', url=group.link_group))
        else:
            markup.add(InlineKeyboardButton(f'❌ {group.name_group}', url=group.link_group))
            text = """Hello, you have the opportunity to participate in every week giveaway. 

Every week we giveaway some fundamental tokens through the subscribers. You have opportunity to win BTC, BNB, ETH, TRX, Polygon. To participate in giveaway, subscribe on following channels and invite at least 5 friends. 

In case of win you will receive message only through this bot! No one will write you DM.

Send join request and after approval press Approve subscription."""
            check = False
            await UsersState.first()
    if check:
        await query.message.answer(text)
        await state.set_state(UsersState.invite_friends)
    else:
        markup.add(InlineKeyboardButton('Approve subscription', callback_data='confirm_subscribe'))
        await query.message.answer(text, reply_markup=markup)
        await UsersState.first()
    SubscribeUsers(user=AllUsers.get(tg_id=str(query.from_user.id)))


async def participate(query: CallbackQuery, state: FSMContext):
    await state.set_state(UsersState.full_user)
    with db_session:
        MembersAirdrop(user=AllUsers.get(tg_id=str(query.from_user.id)))
        commit()
    await query.message.answer('Congratulations, you were registered as participant of every week giveaway. '
                               'You will receive message in case of win!')


async def participate_start(message: Message, state: FSMContext):
    await state.set_state(UsersState.full_user)
    with db_session:
        MembersAirdrop(user=AllUsers.get(tg_id=str(message.from_user.id)))
        commit()
    await message.answer('Congratulations, you were registered as participant of every week giveaway. '
                         'You will receive message in case of win!')
