import pytz
from datetime import datetime, timedelta
import asyncio
from kay import bot


async def seconds_until_date(date):
    print('day_until_birthday')
    data = date
    try:
        date_object = date.split(' ')[1]
    except IndexError:
        data = date + ' 00:00:00'

    timezone = pytz.timezone('Europe/Berlin') # часовой пояс
    current_time = datetime.now(timezone) # реальное время
    # переделываем строку в объект datetime
    target_date_of_birthday = timezone.localize(datetime.strptime(data, '%d.%m.%Y %H:%M:%S'))

    years_have_passed = current_time.year - target_date_of_birthday.year
    years_befor = target_date_of_birthday.year - current_time.year

    if (current_time.month, current_time.day) < (target_date_of_birthday.month, target_date_of_birthday.day):
        years_have_passed -= 1

    next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year)
    if next_date_of_birthday < current_time:
        next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year + 1)

    next_date_of_birthday = next_date_of_birthday - current_time
    days, hours, minutes, seconds = await format_date_of_birthday(next_date_of_birthday)
    seconds_to_wait = (((years_befor if years_befor > 0 else 0) * 31536000) +
                       (days * 86400) + (hours * 3600) + (minutes * 60) + seconds)
    return seconds_to_wait


async def format_date_of_birthday(date_of_birthday):
    print('format_date_of_birthday')
    days = date_of_birthday.days
    hours, remainder = divmod(date_of_birthday.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds


async def notification_message_func(user_id, date_name, seconds):
    print(f'Добавлена в ожидание дата: {date_name}')
    await asyncio.sleep(seconds)
    await bot.send_message(chat_id=user_id, text=f'Здравствуйте 👋\n'
                                                 f'Cпешу вам напомнить 📝 о наступлении '
                                                 f'важной даты:\n'
                                                 f'{date_name}')

