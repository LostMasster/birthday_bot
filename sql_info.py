import pytz
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv("user")
host = os.getenv("host")
password = os.getenv("password")
database = os.getenv("database")


birthd = '31.10.2025'

def day_until_birthday(date):
    data = date + ' 00:00:00'
    timezone = pytz.timezone('Europe/Berlin') # часовой пояс
    current_time = datetime.now(timezone) # реальное время
    # переделываем строку в объект datetime
    target_date_of_birthday = timezone.localize(datetime.strptime(data, '%d.%m.%Y %H:%M:%S'))

    years_have_passed = current_time.year - target_date_of_birthday.year
    years_befor = target_date_of_birthday.year - current_time.year

    if (current_time.month, current_time.day) < (target_date_of_birthday.month, target_date_of_birthday.day):
        years_have_passed -= 1

    if years_have_passed >= 0:

        next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year)
        if next_date_of_birthday < current_time:
            next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year + 1)

        next_date_of_birthday = next_date_of_birthday - current_time
        days, hours, minutes, seconds = format_date_of_birthday(next_date_of_birthday)
        return (f'Лет с указанной даты: {years_have_passed}\n'
                f'До указанной даты: {days}д. {hours}ч. {minutes}м.\n'
                f'Указанная дата рождения: {date}')
    else:
        next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year)
        if next_date_of_birthday < current_time:
            next_date_of_birthday = target_date_of_birthday.replace(year=current_time.year + 1)

        next_date_of_birthday = next_date_of_birthday - current_time
        days, hours, minutes, seconds = format_date_of_birthday(next_date_of_birthday)
        return (f'Назначенный день наступет через: '
                f'{(str(years_befor) + 'л. ') if years_befor > 0 else ''}'
                f'{days}д. {hours}ч. {minutes}м.\n'
                f'Указанная дата: {date}')


def format_date_of_birthday(date_of_birthday):
    days = date_of_birthday.days
    hours, remainder = divmod(date_of_birthday.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return days, hours, minutes, seconds

# print(day_until_birthday(birthd))