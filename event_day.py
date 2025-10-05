import psycopg2
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from date_of_birthd import day_until_birthday
from datetime import datetime
from postgre_sql import connection_pool
import pytz


handler_event_day = Router()

class Event_day(StatesGroup):
    waiting_for_name_event = State()
    waiting_for_date_event = State()
    # waiting_for_finish_event = State()


@handler_event_day.callback_query(lambda c: c.data == 'event_date_list')
async def event_date_list_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    conn = connection_pool.getconn()
    user_id = callback_query.from_user.id
    user_list_text = """"""
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM important_dates WHERE user_id = %s',
                           (user_id,))
            user_db = cursor.fetchall()
            if user_db:
                for data_id, user_id, date_name, event_date, _ in user_db:
                    event_date_str = event_date.strftime('%d.%m.%Y')
                    user_day_to = await day_until_birthday(event_date_str)
                    user_list_text += (f'{date_name}\n{event_date_str}\n{user_day_to}\n\n')
            else:
                button_event_date = InlineKeyboardButton(text='Добавить важную дату',
                                                         callback_data='event_day')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_event_date]])
                await callback_query.message.answer('😞 У вас пока нет записей\n'
                                                    '😃 👇Хотите добавить первую?👇', reply_markup=keyboard)
            await callback_query.message.answer(user_list_text)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL", error)
        finally:
            connection_pool.putconn(conn)
    else:
        print(f"пользователь: {callback_query.from_user.id} Не удалось подключиться к базе данных.")
        await callback_query.message.answer('⚠️Есть проблемы на нашей стороне, попробуйте чуть позже')


@handler_event_day.callback_query(lambda callback: callback.data == 'event_day')
async def event_day_func(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    print('event_day_func')
    await callback_query.message.answer('Придумайте ИМЯ важного дня или события\n'
                                        'К примеру:\n'
                                        '🎂🎁День рождения мамы🎁🎂\n'
                                        'Одним словом такое что бы по названию вы '
                                        'поняли какая это дата👍👀')
    await state.set_state(Event_day.waiting_for_name_event)


@handler_event_day.message(Event_day.waiting_for_name_event)
async def waiting_for_name_event_func(message: Message, state: FSMContext):
    print('waiting_for_name_event_func')
    button = InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel_delete')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    if len(message.text) <= 255:
        await state.update_data(event_day_name=message.text)
        current_state = await state.get_state()
        print(f'Состояние {current_state}')
        await state.set_state(Event_day.waiting_for_date_event)
        current_state = await state.get_state()
        print(f'Состояние {current_state}')
        await message.answer('📆 Введите пожалуйста дату в формане ДД.ММ.ГГ\n'
                             '(день-01.месяц-01.год-2001)\n'
                             '👉пример: 01.01.2001', reply_markup=keyboard)
    else:
        await message.answer('😞Максимально я могу запомнить не более 255 символов, '
                             'попробуйте сократить пожалуйста😊', reply_markup=keyboard)


async def validate_and_format_date(date_input: str) -> str:
    # Возможные форматы ввода
    date_formats = ['%d.%m.%Y', '%d,%m,%Y', '%d-%m-%Y', '%d %m %Y', '%d/%m/%Y']
    parsed_date = None

    for date_format in date_formats:
        try:
            # Пытаемся преобразовать строку в дату
            parsed_date = datetime.strptime(date_input, date_format)
            # Возвращаем дату в нужном формате
            return parsed_date.strftime('%d.%m.%Y')
        except ValueError:
            # Если не удалось преобразовать, переходим к следующему формату
            continue
    if not parsed_date:
        return 'error'
    # Если ни один формат не подошёл, возвращаем сообщение об ошибке
    # raise ValueError("Неверный формат даты или несуществующая дата. Попробуйте ещё раз.")


@handler_event_day.message(Event_day.waiting_for_date_event)
async def waiting_for_date_event_func(message: Message, state: FSMContext):
    print('waiting_for_date_event_func')
    user_date = await validate_and_format_date(message.text)
    print(str(user_date))
    print(type(user_date))
    try:
        if datetime.strptime(user_date, '%d.%m.%Y'):
            await state.update_data(event_day_date=message.text)
            print(message.text)
            # await state.set_state(Event_day.waiting_for_finish_event)
            user_data = await state.get_data()
            print(f'Дата важного дня сохранена {user_data['event_day_date'], user_data['event_day_name']}')
            # current_state = await state.get_state()
            # print(f'Состояние {current_state}')
            # await message.answer('Скажи да')

        timesone = pytz.timezone('Europe/Berlin')
        obj_time = datetime.now(timesone)
        time_now = obj_time.strftime('%d.%m.%Y %H:%M:%S')

        conn = connection_pool.getconn()

        user_data = await state.get_data()
        data_id = time_now
        user_id = message.from_user.id
        date_name = user_data['event_day_name']
        event_date = user_data['event_day_date']
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT (*) FROM important_dates WHERE user_id = %s', (user_id,))
                record_exists = cursor.fetchone()[0] > 0
                if not record_exists:
                    # Вставка новой записи
                    cursor.execute('INSERT INTO important_dates (data_id, user_id, date_name,'
                                   'event_date) VALUES (%s, %s, %s, %s)',
                                   (data_id, user_id, date_name, event_date))
                    print(f'Новый пользователь {user_id} добавлен')
                else:
                    # обновление существующей записи
                    cursor.execute('INSERT INTO important_dates (data_id, user_id, date_name,'
                                   ' event_date) VALUES (%s, %s, %s, %s)',
                                   (data_id,user_id, date_name, event_date))
                    print(f'Данные пользователя {user_id} обновлены')
                conn.commit()
                cursor.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"пользователь: {message.from_user.id} Ошибка при работе с PostgreSQL", str(error))
            finally:
                connection_pool.putconn(conn)
        else:
            print(f"пользователь: {message.from_user.id} Не удалось подключиться к базе данных.")
            await message.answer('😞Извините попробуйте позже добавить '
                                 'дату похоже меня ремонтируют')
        await state.clear()
        await message.answer('🥳 Спасибо я запомнил вашу 📅 дату')
    except ValueError:
        await message.answer('Введите дату в доступних мне форматах пожалуйста😇\n'
                             '🫣 Другие я к сожалению не понимаю \n'
                             'Вот 👇 примеры:\n'
                             '01.01.2001\n'
                             '01,01,2001\n'
                             '01-01-2001\n'
                             '01 01 2001\n'
                             '01/01/2001')



# @handler_event_day.message(Event_day.waiting_for_finish_event)
# async def finish_event_func(message: Message, state: FSMContext):
#     print("finish_event_func")
#     timesone = pytz.timezone('Europe/Berlin')
#     obj_time = datetime.now(timesone)
#     time_now = obj_time.strftime('%d.%m.%Y %H:%M:%S')
#
#     conn = connection_pool.getconn()
#
#     user_data = await state.get_data()
#     data_id = time_now
#     user_id = message.from_user.id
#     date_name = user_data['event_day_name']
#     event_date = user_data['event_day_date']
#     if conn:
#         try:
#             cursor = conn.cursor()
#             cursor.execute('SELECT COUNT (*) FROM important_dates WHERE user_id = %s', (user_id,))
#             record_exists = cursor.fetchone()[0] > 0
#             if not record_exists:
#                 # Вставка новой записи
#                 cursor.execute('INSERT INTO important_dates (data_id, user_id, date_name,'
#                                'event_date) VALUES (%s, %s, %s, %s)',
#                                (data_id, user_id, date_name, event_date))
#                 print(f'Новый пользователь {user_id} добавлен')
#             else:
#                 # обновление существующей записи
#                 cursor.execute('INSERT INTO important_dates (data_id, user_id, date_name,'
#                                ' event_date) VALUES (%s, %s, %s, %s)',
#                                (data_id,user_id, date_name, event_date))
#                 print(f'Данные пользователя {user_id} обновлены')
#             conn.commit()
#             cursor.close()
#         except (Exception, psycopg2.DatabaseError) as error:
#             print("Ошибка при работе с PostgreSQL", error)
#         finally:
#             connection_pool.putconn(conn)
#     else:
#         print("Не удалось подключиться к базе данных.")
#     await state.clear()
#     await message.answer('Запись добавлена')