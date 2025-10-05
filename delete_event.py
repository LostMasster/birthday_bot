from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from aiogram import Router
import psycopg2
from postgre_sql import connection_pool
from aiogram.fsm.context import FSMContext
from datetime import datetime


handler_delete_event = Router()


@handler_delete_event.callback_query(lambda c: c.data == 'delete_event')
async def delete_event_command(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    conn = connection_pool.getconn()
    user_id = callback_query.from_user.id
    print(user_id)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM important_dates WHERE user_id = %s', (user_id,))
            user_db = cursor.fetchall()
            if user_db:
                buttons = [[InlineKeyboardButton(text=f'❌ {date_name}',
                                                 callback_data=f'delete_event,{data_id}')]
                           for data_id, user_id, date_name, event_date, _ in user_db
                           ]
                buttons.append([InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel_delete')])
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                cursor.close()
                await callback_query.message.answer(f'Выберите из списка👇 что хотите ❌ удалить',
                                                    reply_markup=keyboard)
            else:
                button_event_date = InlineKeyboardButton(text='Добавить важную дату',
                                                         callback_data='event_day')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_event_date]])
                await callback_query.message.answer('😞 У вас пока нет записей\n'
                                                    '😃 👇Хотите добавить первую?👇', reply_markup=keyboard)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL", str(error))
            await callback_query.message.answer('⚠️Извините произошла ошибка, попробуйте еще раз')
        finally:
            connection_pool.putconn(conn)
    else:
        print("Не удалось подключиться к базе данных.")
        await callback_query.message.answer('⚠️Есть проблемы на нашей стороне, попробуйте чуть позже')


@handler_delete_event.callback_query(lambda c: c.data.startswith('delete_event,'))
async def delete_event_func(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    print('delete_event_func')
    data_id = callback_query.data.split(',')[1] # Извлекаем data_id пользователя
    data_id_d = datetime.strptime(data_id, '%Y-%m-%d %H:%M:%S')

    user_id = callback_query.from_user.id

    conn = connection_pool.getconn()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM important_dates WHERE user_id = %s AND data_id = %s",
                           (user_id, data_id_d.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            cursor.close()
            await callback_query.message.answer('Дата успешно удалена')
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL", error)
            await callback_query.message.answer('Извините произошла ошибка, попробуйте еще раз')
        finally:
            connection_pool.putconn(conn)
    else:
        print(f"пользователь: {callback_query.from_user.id} Не удалось подключиться к базе данных.")
        await callback_query.message.answer('Есть проблемы на нашей стороне, попробуйте чуть позже')


@handler_delete_event.callback_query(lambda c: c.data == 'cancel_delete')
async def cancel_delete_func(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    current_state = await state.get_state()
    print(current_state)
    if current_state:
        await state.clear()