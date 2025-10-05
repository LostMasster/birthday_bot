import asyncio

from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router
import psycopg2
from postgre_sql import connection_pool
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from Calendar import create_calendar


handler_change_date = Router()


@handler_change_date.callback_query(lambda c: c.data == 'replace_data')
async def change_date_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    conn = connection_pool.getconn()
    user_id = callback_query.from_user.id
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM important_dates WHERE user_id = %s',(user_id,)
                           )
            user_db = cursor.fetchall()
            if user_db:
                buttons = [[InlineKeyboardButton(text=f'♻️ {date_name}',
                                                 callback_data=f'change,{data_id}')]
                           for data_id, user_id, date_name, event_date, _ in user_db
                           ]
                buttons.append([InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel_delete')])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                cursor.close()
                await callback_query.message.answer('🫵 Выберите пожалуйста дату которую хотите ♻️ изменить',
                                                    reply_markup=keyboard)
            else:
                button_event_date = InlineKeyboardButton(text='Добавить важную дату',
                                                         callback_data='event_day')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_event_date]])
                await callback_query.message.answer('😞 У вас пока нет записей\n'
                                                    '😃 👇Хотите добавить первую?👇',
                                                    reply_markup=keyboard)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL",
                  str(error))
        finally:
            connection_pool.putconn(conn)
    else:
        print(f"пользователь: {callback_query.from_user.id} Не удалось подключиться к"
              f" базе данных.")
        await callback_query.message.answer('⚠️ Есть проблемы на нашей стороне, попробуйте'
                                            ' чуть позже')


@handler_change_date.callback_query(lambda c: c.data.startswith('change,'))
async def change_event_func (callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    data_id = callback_query.data.split(',')[1] # Извлекаем data_id пользователя
    buttons = [[InlineKeyboardButton(text='♻️ Изменить название даты',
                                     callback_data=f'change_date_name,{data_id}')],
               [InlineKeyboardButton(text='♻️ Изменить дату',
                                    callback_data=f'change_date,{data_id}')]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer('Выберите что именно хотите ♻️ изменить',
                                       reply_markup=keyboard)


class Change(StatesGroup):
    waiting_for_data = State()


@handler_change_date.callback_query(lambda c: c.data.startswith(('change_date_name,', 'change_date,')))
async def change_event_func_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    method, data_id = callback_query.data.split(',')
    await state.update_data(method=method, data_id=data_id)
    await state.set_state(Change.waiting_for_data)
    status = await state.get_state()
    print(f'Sejchas status {status}')
    print(type(status))
    if method == 'change_date_name':
        await callback_query.message.answer('⌨️ Введите пожалуйста новое название для 📆 даты:')
    else:
        print('calendar')
        await callback_query.message.answer("Выберите дату:",
                                            reply_markup=await create_calendar())
        # await callback_query.message.answer('Введите дату в доступних мне форматах пожалуйста😇\n'
        #                                     '🫣 Другие я к сожалению не понимаю \n'
        #                                     'Вот 👇 примеры:\n'
        #                                     '01.01.2001\n'
        #                                     '01,01,2001\n'
        #                                     '01-01-2001\n'
        #                                     '01 01 2001\n'
        #                                     '01/01/2001')


@handler_change_date.message(Change.waiting_for_data)
async def change_event_func_start_update(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id
    method = user_data['method']
    data_id = user_data['data_id']
    conn = connection_pool.getconn()

    if method == 'change_date_name':
        if len(message.text) <= 255:
            if conn:
                try:
                    new_date_name = message.text
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE important_dates SET date_name = %s WHERE user_id = %s AND data_id = %s',
                        (new_date_name, user_id, data_id)
                    )
                    conn.commit()
                    cursor.close()
                    await message.answer('🥳 Вы успешно изменили название')
                except (Exception, psycopg2.DatabaseError) as error:
                    print(f"пользователь: {message.from_user.id} Ошибка при работе с PostgreSQL", str(error))
                finally:
                    connection_pool.putconn(conn)
            else:
                print(f"пользователь: {message.from_user.id} Не удалось подключиться к базе данных.")
                await message.answer('⚠️Извините попробуйте позже изменить название даты')
        else:
            await message.answer('⚠️К сожалению длинна названия даты не может'
                                 ' быть более чем 255 символов 🥺')
    # if method == 'change_date':

        # try:
        #     if datetime.strptime(message.text, '%d.%m.%Y'):
        #         new_date = message.text
        #         if conn:
        #             try:
        #                 cursor = conn.cursor()
        #                 cursor.execute(
        #                     'UPDATE important_dates SET event_date = %s WHERE user_id = %s AND data_id = %s',
        #                     (new_date, user_id, data_id)
        #                 )
        #                 conn.commit()
        #                 cursor.close()
        #                 await message.answer('🥳 Вы успешно изменили 📅 дату')
        #             except (Exception, psycopg2.DatabaseError) as error:
        #                 print(f"пользователь: {message.from_user.id} Ошибка при работе с PostgreSQL", str(error))
        #             finally:
        #                 connection_pool.putconn(conn)
        #         else:
        #             print(f"пользователь: {message.from_user.id} Не удалось подключиться к базе данных.")
        #             await message.answer('⚠️Извините похоже у меня проблемы но я уже сообщил об этом!')
        # except ValueError:
        #     await message.answer('Введите дату в доступних мне форматах пожалуйста😇\n'
        #                          '🫣 Другие я к сожалению не понимаю \n'
        #                          'Вот 👇 примеры:\n'
        #                          '01.01.2001\n'
        #                          '01,01,2001\n'
        #                          '01-01-2001\n'
        #                          '01 01 2001\n'
        #                          '01/01/2001')

