import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from kay import bot
import psycopg2
import pytz
from datetime import datetime
from postgre_sql import connection_pool
import calendar
from Calendar import create_calendar
from notification import seconds_until_date, notification_message_func

handler_with_hours = Router()


class Waiting(StatesGroup):
    waiting_for_name_event = State()


# @handler_with_hours.message()
# async def send_message_to_id(message: Message):
#     button = [[InlineKeyboardButton(text='Перейти на бота', url='https://t.me/Birthday_sink_bot')]]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=button)
#     await bot.send_message(chat_id=message.chat.id,
#                            message_thread_id=message.message_thread_id,
#                            text='Чтобы перейти к боту, нажмите на кнопку ниже',
#                            reply_markup=keyboard)



async def create_watch(data_id, h=12, m=00):
    buttons = []
    time_list = ['0️⃣0️⃣', '0️⃣1️⃣', '0️⃣2️⃣', '0️⃣3️⃣', '0️⃣4️⃣', '0️⃣5️⃣', '0️⃣6️⃣', '0️⃣7️⃣', '0️⃣8️⃣', '0️⃣9️⃣',
                 '1️⃣0️⃣', '1️⃣1️⃣', '1️⃣2️⃣', '1️⃣3️⃣', '1️⃣4️⃣', '1️⃣5️⃣', '1️⃣6️⃣', '1️⃣7️⃣', '1️⃣8️⃣', '1️⃣9️⃣',
                 '2️⃣0️⃣', '2️⃣1️⃣', '2️⃣2️⃣', '2️⃣3️⃣', '2️⃣4️⃣', '2️⃣5️⃣', '2️⃣6️⃣', '2️⃣7️⃣', '2️⃣8️⃣', '2️⃣9️⃣',
                 '3️⃣0️⃣', '3️⃣1️⃣', '3️⃣2️⃣', '3️⃣3️⃣', '3️⃣4️⃣', '3️⃣5️⃣', '3️⃣6️⃣', '3️⃣7️⃣', '3️⃣8️⃣', '3️⃣9️⃣',
                 '4️⃣0️⃣', '4️⃣1️⃣', '4️⃣2️⃣', '4️⃣3️⃣', '4️⃣4️⃣', '4️⃣5️⃣', '4️⃣6️⃣', '4️⃣7️⃣', '4️⃣8️⃣', '4️⃣9️⃣',
                 '5️⃣0️⃣', '5️⃣1️⃣', '5️⃣2️⃣', '5️⃣3️⃣', '5️⃣4️⃣', '5️⃣5️⃣', '5️⃣6️⃣', '5️⃣7️⃣', '5️⃣8️⃣', '5️⃣9️⃣']
    buttons.append([
        InlineKeyboardButton(text='+10 Часов', callback_data=f'hours_10_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='+10 Минут', callback_data=f'minutes_10_{h}_{m}_{data_id}'),
                    ])
    buttons.append([
        InlineKeyboardButton(text='+5 Часов', callback_data=f'hours_5_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='+5 Минут', callback_data=f'minutes_5_{h}_{m}_{data_id}'),
                    ])
    buttons.append([
        InlineKeyboardButton(text='+1 Час', callback_data=f'hours_1_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='+1 Минута', callback_data=f'minutes_1_{h}_{m}_{data_id}'),
                    ])
    buttons.append([
        InlineKeyboardButton(text=f'🕐{time_list[h]}:{time_list[m]}🕑', callback_data='ignore')
        # InlineKeyboardButton(text=f'🕐{0 if h < 10 else ''}{h}:{0 if m < 10 else ''}{m}🕑',
        #                      callback_data='ignore')
                    ])
    buttons.append([
        InlineKeyboardButton(text='-1 Час', callback_data=f'hours_-1_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='-1 Минута', callback_data=f'minutes_-1_{h}_{m}_{data_id}'),
    ])
    buttons.append([
        InlineKeyboardButton(text='-5 Часов', callback_data=f'hours_-5_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='-5 Минут', callback_data=f'minutes_-5_{h}_{m}_{data_id}'),
    ])
    buttons.append([
        InlineKeyboardButton(text='-10 Часов', callback_data=f'hours_-10_{h}_{m}_{data_id}'),
        InlineKeyboardButton(text='-10 Минут', callback_data=f'minutes_-10_{h}_{m}_{data_id}'),
    ])
    buttons.append([
        InlineKeyboardButton(text='✅ Сохранить время напоминания ✅',
                             callback_data=f'time_accept-{h}-{m}-{data_id}')
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@handler_with_hours.callback_query(lambda c: c.data.startswith(('hours_', 'minutes_')))
async def watch_keyboard_func(callback_query: CallbackQuery):
    method, num, h, m, data_id = callback_query.data.split('_')
    num = int(num)
    h = int(h)
    m = int(m)
    if method == 'hours':
        print('1')
        if num > 0:
            print('2')
            for _ in range(num):
                print('3')
                h += 1
                if h > 23:
                    h = 0
        else:
            print('4')
            for _ in range(abs(num)):
                print('5')
                h -= 1
                if h < 0:
                    h = 23
    else:
        if num < 0:
            for _ in range(abs(num)):
                m -= 1
                if m < 0: m = 59
        else:
            for _ in range(num):
                m += 1
                if m > 59: m = 0

    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_watch(data_id, h, m))


@handler_with_hours.callback_query(lambda c: c.data == 'date_with_hours')
async def date_with_hours_func(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    print('event_day_func')
    await callback_query.message.answer('Придумайте ИМЯ важного дня или события\n'
                                        'К примеру:\n'
                                        '🎂🎁День рождения Йоулупукки🎁🎂\n'
                                        'Одним словом такое что бы по названию вы '
                                        'поняли какая это дата👍👀')
    await state.set_state(Waiting.waiting_for_name_event)


@handler_with_hours.message(Waiting.waiting_for_name_event)
async def waiting_for_name_event_func(message: Message, state: FSMContext):
    if len(message.text) <= 255:
        await state.update_data(event_day_name=message.text)
    else:
        await message.answer('😞Максимально я могу запомнить не более 255 символов, '
                             'попробуйте сократить пожалуйста😊')
    await message.answer("Выберите нужную дату пожалуйста 😊",
                         reply_markup=await create_calendar())


@handler_with_hours.callback_query(lambda c: c.data.startswith('set_time_notification_'))
async def set_time_notification_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    data_id = callback_query.data.split('_')[3]
    await callback_query.message.answer('Установите время когда мне отправить'
                                        ' вам ⏰ сообщение с напоминание к указанной 📅 дате',
                                        reply_markup=await create_watch(data_id))


@handler_with_hours.callback_query(lambda c: c.data.startswith('time_accept-'))
async def time_accept_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    h, m, data_id = callback_query.data.split('-')[1:]
    conn = connection_pool.getconn()
    user_id = callback_query.from_user.id
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT date_name, event_date FROM important_dates WHERE user_id = %s AND data_id = %s',
                (user_id, data_id)
            )
            date_name, event_date = cursor.fetchone()
            event_date_str = datetime.strftime(event_date, '%d.%m.%Y')
            seconds = await seconds_until_date(f'{event_date_str} {0 if int(h) < 10 else ''}{h}:{0 if int(m) < 10 else ''}{m}:00')

            cursor2 = conn.cursor()
            cursor2.execute(
                'UPDATE important_dates SET notification = %s WHERE user_id = %s '
                'AND data_id = %s', (f'{0 if int(h) < 10 else ''}{h}:'
                                     f'{0 if int(m) < 10 else ''}{m}:00', user_id, data_id)
            )
            conn.commit()
            await callback_query.message.answer('🥳 Я запомнил когда вам отправить'
                                                ' напоминание, спасибо 😊')
            if seconds < 43200:
                await asyncio.create_task(notification_message_func(user_id, date_name, seconds))
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL", str(error))
        finally:
            connection_pool.putconn(conn)
    else:
        print(f"пользователь: {callback_query.from_user.id} Не удалось подключиться к базе данных.")
        await callback_query.message.answer('⚠️Извините попробуйте позже изменить название даты')
