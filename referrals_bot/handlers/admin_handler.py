import csv

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.utils.exceptions import ChatNotFound
from pony.orm import db_session, commit

from models import Groups, AllUsers, MembersAirdrop
from states.state import AddGroups
from referrals_bot import bot


@db_session
async def list_groups(message: Message, state: FSMContext):
    markup = InlineKeyboardMarkup(row_width=2)
    all_group = Groups.select()
    if not all_group:
        text = 'Нет групп для подписки!'
    else:
        text = 'Список групп для подписки:'
    for group in all_group:
        markup.add(InlineKeyboardButton(f'{group.name_group}', url=group.link_group),
                   InlineKeyboardButton('Удалить канал', callback_data=f'delete_channel_{group.id_group}'))
    markup.add(InlineKeyboardButton('Добавить группу!', callback_data='add_group'))
    await message.answer(text, reply_markup=markup)


@db_session
async def add_group(query: CallbackQuery, state: FSMContext):
    await AddGroups.first()
    await query.message.answer(
        'Чтобы добавить группу, добавьте бота в канал и пришлите сюда ссылку в формате (@channel) или '
        'id канала')


@db_session
async def get_id_channel(message: Message, state: FSMContext):
    try:
        try:
            text = int(message.text)
        except Exception:
            text = message.text
        channel = await bot.get_chat(text)
    except ChatNotFound:
        await message.answer('К сожалению, данный канал не был найден!\nВозможно вы не добавили бота в канал!')
        return
    group_from_db = Groups.get(id_group=str(channel.id))
    if not group_from_db:
        link = await bot.create_chat_invite_link(channel.id, creates_join_request=True)
        Groups(
            id_group=str(channel.id),
            link_group=link.invite_link,
            name_group=channel.full_name
        )
        commit()
        await message.answer('Группа успешно добавлена!')
    else:
        await message.answer('Данная группа уже существует в базе!')
    await state.finish()


async def delete_channel(query: CallbackQuery, state: FSMContext):
    id_channel = query.data.split('delete_channel_')[1]
    with db_session:
        Groups.get(id_group=id_channel).delete()
    await query.message.answer('Группа успешно удалена!')


@db_session
async def get_all_user(message: Message, state: FSMContext):
    with open('all_user.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for user in AllUsers.select():
            try:
                writer.writerow([user.tg_id])
            except Exception as err:
                continue
    file = InputFile('all_user.csv', filename='all_user.csv')
    await message.answer_document(file)


@db_session
async def get_suit_user(message: Message, state: FSMContext):
    with open('suit_user.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        for user in MembersAirdrop.select():
            try:
                writer.writerow([user.user.tg_id])
            except Exception as err:
                continue
    file = InputFile('suit_user.csv', filename='suit_user.csv')
    await message.answer_document(file)
