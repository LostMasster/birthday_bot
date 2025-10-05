from aiogram.filters import CommandStart, Command
from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import pytz
from postgre_sql import new_user, connection_pool
import psycopg2


handler_command = Router()

@handler_command.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext):
    print('command_start')
    timesone = pytz.timezone('Europe/Berlin')
    obj_time = datetime.now(timesone)
    time_now = obj_time.strftime('%d.%m.%Y %H:%M:%S')

    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ''
    date_of_register = time_now

    await new_user(user_id, first_name, last_name, date_of_register)

    button_event_date = InlineKeyboardButton(text='Добавить важную дату',
                                             callback_data='date_with_hours')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_event_date]])
    await message.answer(f'👋Здравствуйте {first_name} {last_name} Я ваш бот🤖 помошник\n'
                         f'Вы можете написать мне важную☝️ дату,\n'
                         f'На пример:\n '
                         f'День рождения прабабушки\n'
                         f'14.09.1940\n\''
                         f'Я ее запомню🧐\n'
                         f'📝 И смогу сказать \n'
                         f'⏳ Через сколько времени наступит следующая дата\n'
                         f'⌛️ И сколько времени прошло с указанной даты\n'
                         f'🎂 Если это к примеру день рождения \n'
                         f'🤵‍♂️👰‍♀️ Или годовщина свадьбы, \n'
                         f'⏰ Так же я вам буду напомнать когда останется несколько дней до'
                         f' указанной даты\n'
                         f'Так же вы можете воспользоватьmся кнопкой 🟦 Menu с лева от поля ввода для навигации\n'
                         f'Нажмите на 👇кнопку👇 что бы записать вашу дату ',
                         reply_markup=keyboard)


@handler_command.message(Command('menu'))
async def menu_func(message: Message):
    buttons = [# [InlineKeyboardButton(text='✅ Добавить важную дату', callback_data='event_day')],
               [InlineKeyboardButton(text='✅⏰ Добавить Дату', callback_data='date_with_hours')],
               [InlineKeyboardButton(text='♻️ Изменить дату',callback_data='replace_data')],
               [InlineKeyboardButton(text='📋 Показать список важных дней', callback_data='event_date_list')],
               [InlineKeyboardButton(text='❌ Удалить из списка', callback_data='delete_event')],
               [InlineKeyboardButton(text='⚙️ Настройка уведомлений', callback_data='notification_settings')]
               ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(f'👋Добро пожаловать в мое меню ☺️ {message.from_user.first_name} '
                         f'{message.from_user.last_name if message.from_user.last_name else ''} \n'
                         f'Выберите пожалуйста что вам интересно', reply_markup=keyboard)








@handler_command.message(Command('add_event_date'))
async def add_event_date_func(message: Message):
    button_add_event = InlineKeyboardButton(text='Добавить важную дату', callback_data='event_day')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_add_event]])
    await message.answer('Что бы продолжить нажмите пожалуйста на кнопку \n'
                         '👇"Добавить важную дату"👇', reply_markup=keyboard)



