from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from datetime import datetime
from postgre_sql import connection_pool
import pytz
import psycopg2
import calendar
from kay import bot


handler_calendar = Router()


async def create_month_choice_button(year):
    # создание кнопок для выбора месяца
    buttons = []
    month_names = ['', 'Январь', 'Февраль', "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    x = 0
    for i in range(4):
        row = []
        for i in range(3):
            x += 1
            row.append(InlineKeyboardButton(text=month_names[x], callback_data=f'number-of-month-{year}-{x}'))

        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def create_year_choice_func(year=None, month=1):
    # создаем кнопки для выбора года
    now = datetime.now()
    if year is None: year = now.year

    # Создаем пустой список для кнопок календаря
    buttons = []

    buttons.append([
        InlineKeyboardButton(text='<<', callback_data=f'<<-year-{year}-{month}') if int(year) >= 0 else 'ignore',
        InlineKeyboardButton(text='>>', callback_data=f'>>-year-{year}-{month}')
    ])
    year_row = year - 19
    for i in range(5):
        row = []
        for i in range(5):
            row.append(InlineKeyboardButton(text=f'{year_row if int(year_row) > 0 else ''}',
                                            callback_data=f'choice-year-{year_row}-{month}'))
            year_row += 1
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Создание календаря для выбора даты
async def create_calendar(year=None, month=None):
    now = datetime.now()
    if year is None: year = now.year
    if month is None: month = now.month
    month_names = ['', 'Январь', 'Февраль', "Март", "Апрель", "Май", "Июнь",
                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]

    # Создаем пустой список для кнопок календаря
    buttons = []

    buttons.append([
        InlineKeyboardButton(text='<<', callback_data=f'prev-year-{year}-{month}'),
        InlineKeyboardButton(text=f'{year}', callback_data=f'year-choice-{year}-{month}'),
        InlineKeyboardButton(text='>>', callback_data=f'next-year-{year}-{month}')
    ])

    # строка с названием месяца и кнопками навигации
    buttons.append([
        InlineKeyboardButton(text='<<', callback_data=f'prev-month-{year}-{month}'),
        InlineKeyboardButton(text=f'{month_names[month]}',
                             callback_data=f'month-choice-{year}-{month}'),
        InlineKeyboardButton(text='>>', callback_data=f'next-month-{year}-{month}')
    ])

    # Дни недели
    week_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    buttons.append([InlineKeyboardButton(text=day, callback_data='ignore') for day in week_days])

    # Календарь
    month_calendar = calendar.monthcalendar(year, month)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=' ', callback_data='ignore'))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f'day-{day}-{year}-{month}'))
        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@handler_calendar.callback_query(lambda c: c.data.startswith('number-of-month-'))
async def number_of_month_choice(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    year, month = callback_query.data.split('-')[3:]
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(int(year),int(month)))


@handler_calendar.callback_query(lambda c: c.data.startswith('month-choice-'))
async def month_choice_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    year= callback_query.data.split('-')[2]

    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_month_choice_button(year))


@handler_calendar.callback_query(lambda c: c.data == 'calendar')
async def send_welcome(message: Message):
    await message.answer("Выберите дату:", reply_markup=await create_calendar())


@handler_calendar.callback_query(lambda c: c.data.startswith('year-choice-'))
async def year_choice_func(callback_query: CallbackQuery):
    year, month = callback_query.data.split('-')[2:]
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_year_choice_func(int(year), int(month)))


@handler_calendar.callback_query(lambda c: c.data.startswith('<<-year-'))
async def minus_years_func(callback_query: CallbackQuery):
    year = int(callback_query.data.split('-')[2]) - 25
    month = int(callback_query.data.split('-')[3])
    print(f'minus_year_func {year}')
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_year_choice_func(year, month))


@handler_calendar.callback_query(lambda c: c.data.startswith('>>-year-'))
async def plus_years_func(callback_query: CallbackQuery):
    year = int(callback_query.data.split('-')[2]) + 25
    month = int(callback_query.data.split('-')[3])
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_year_choice_func(year, month))


@handler_calendar.callback_query(lambda c: c.data.startswith('choice-year-'))
async def choice_year__func(callback_query: CallbackQuery):
    year, month = callback_query.data.split('-')[2:]
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(year=int(year),
                                                                           month=int(month)))

@handler_calendar.callback_query(lambda c: c.data and c.data.startswith('prev-year-'))
async def process_next_month(callback_query: CallbackQuery):
    year, month = map(int, callback_query.data.split('-')[2:])
    year -= 1
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(year, month))


@handler_calendar.callback_query(lambda c: c.data and c.data.startswith('next-year-'))
async def process_next_month(callback_query: CallbackQuery):
    year, month = map(int, callback_query.data.split('-')[2:])
    year += 1
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(year, month))


@handler_calendar.callback_query(lambda c: c.data and c.data.startswith('prev-month-'))
async def process_prev_month(callback_query: CallbackQuery):
    year, month = map(int, callback_query.data.split('-')[2:])
    if month == 1:
        month = 12
        year -= 1
    else:
        month -= 1
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(year, month))


@handler_calendar.callback_query(lambda c: c.data and c.data.startswith('next-month-'))
async def process_next_month(callback_query: CallbackQuery):
    year, month = map(int, callback_query.data.split('-')[2:])
    if month == 12:
        month = 1
        year += 1
    else:
        month += 1
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=await create_calendar(year, month))


@handler_calendar.callback_query(lambda c: c.data and c.data.startswith('day-'))
async def process_day(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    day, year, month = map(int, callback_query.data.split('-')[1:])
    selected_date = datetime(year, month, day)
    selected_date_str = selected_date.strftime("%d.%m.%Y")
    buttons = [
        [InlineKeyboardButton(text='✅ Да подтверждаю', callback_data=f'calendar_accept,{selected_date_str}')],
        [InlineKeyboardButton(text='❌ Нет,♻️ изменить', callback_data='calendar_no')],
        [InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel_delete')]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(f'Вы выбрали 📆 дату: {selected_date_str}',
                                        reply_markup=keyboard)


@handler_calendar.callback_query(lambda c: c.data == 'calendar_no')
async def calendar_no_func(callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.message.answer('Выберите нужную дату пожалуйста 😊',
                                        reply_markup=await create_calendar())


@handler_calendar.callback_query(lambda c: c.data == 'ignore')
async def process_ignore(callback_query: CallbackQuery):
    await callback_query.answer()


@handler_calendar.callback_query(lambda c: c.data.startswith('calendar_accept,'))
async def calendar_yes_func(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    user_date = callback_query.data.split(',')[1]

    await state.update_data(event_date=user_date)

    timesone = pytz.timezone('Europe/Berlin')
    obj_time = datetime.now(timesone)
    time_now = obj_time.strftime('%d.%m.%Y %H:%M:%S')

    conn = connection_pool.getconn()
    status = await state.get_state()
    user_data = await state.get_data()
    data_id = user_data['data_id'] if status == 'Change:waiting_for_data' else time_now
    if conn:
        try:
            if status == 'Change:waiting_for_data':
                print(status)
                print(f'Календарь {status}')
                user_id = callback_query.from_user.id
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE important_dates SET event_date = %s WHERE user_id = %s AND data_id = %s',
                    (user_date, user_id, data_id)
                )
                conn.commit()
                cursor.close()
                # await callback_query.message.answer('🥳 Вы успешно изменили 📅 дату')
            else:
                print(status)
                print('kalendar zapisuet novuju stroku')
                user_id = callback_query.from_user.id
                date_name = user_data['event_day_name']
                event_date = user_data['event_date']
                cursor = conn.cursor()
                # вставка записи
                cursor.execute('INSERT INTO important_dates (data_id, user_id, date_name,'
                               ' event_date) VALUES (%s, %s, %s, %s)',
                               (data_id, user_id, date_name, event_date))
                print(f'Данные пользователя {user_id} обновлены')
                conn.commit()
                cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"пользователь: {callback_query.from_user.id} Ошибка при работе с PostgreSQL", str(error))
        finally:
            connection_pool.putconn(conn)
    else:
        print(f"пользователь: {callback_query.from_user.id} Не удалось подключиться к базе данных.")
        await callback_query.message.answer('😞Извините попробуйте позже добавить '
                                            'дату похоже меня ремонтируют')
    try:
        date_name = user_data['event_day_name']
        button = InlineKeyboardButton(text='Добавить',
                                      callback_data=f'set_notif_{data_id}_{date_name}')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

        await state.clear()
        await callback_query.message.answer('🥳 Спасибо я запомнил вашу 📅 дату\n'
                                            'Хотите добавить ⏰ напоминание к дате?👇',
                                            reply_markup=keyboard)
    except KeyError as e:
        print('Поле event_day_name пустое, ВЕРОЯТНО попытка изменить дату события')

