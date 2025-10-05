from datetime import datetime, timedelta
from kay import tg_bot_api, bot
import asyncio
import pytz
import psycopg2
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from handler_command import handler_command
from date_of_birthd import handler_date_of_birthday
from postgre_sql import connection_pool
from event_day import handler_event_day
from delete_event import handler_delete_event
from change_date import handler_change_date
from Calendar import handler_calendar
from date_with_hours import handler_with_hours
from notification import seconds_until_date, notification_message_func


# bot = Bot(token=tg_bot_api)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

async def on_shutdown(dp):
    connection_pool.closeall()
    print("Пул соединений закрыт")


# Функция для расчета времени до запуска
def time_until(hour, minute, timezone='Europe/Warsaw'):
    now = datetime.now(pytz.timezone(timezone))
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Если целевое время уже прошло, устанавливаем его на следующий день
    if now >= target_time:
        target_time += timedelta(days=1)

    return (target_time - now).total_seconds()


async def run_checking_notification():
    while True:
        # Вычисляем время до следующего запуска
        wait_seconds_to_check1 = time_until(18, 57)  # Указываем время проверки актуальных уведомлений
        wait_seconds_to_check2 = time_until(12, 0)
        print(f"Ожидание до следующего запуска: \n"
              f"Полноч {wait_seconds_to_check1} секунд до запуска\n"
              f"Полдень {wait_seconds_to_check2} секунд до запуска")
        await asyncio.sleep(wait_seconds_to_check1
                            if wait_seconds_to_check1 < wait_seconds_to_check2
                            else wait_seconds_to_check2)  # Ожидаем до целевого времени
        # Выполняем задачу
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM important_dates'
        )
        database = cursor.fetchall()
        if database:
            try:
                for data_id, user_id, date_name, event_date, notification in database:
                    event_date_str = event_date.strftime('%d.%m.%Y')
                    seconds = await seconds_until_date(f'{event_date_str}{' ' if notification != 'None' else ''}'
                                                       f'{notification if notification != 'None' else ''}')
                    if seconds < 43200:
                        print('ОТПРАВКА')
                        await notification_message_func(user_id, date_name, seconds)
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"пользователь: Ошибка при работе с PostgreSQL", error)
            finally:
                connection_pool.putconn(conn)


async def main():
    print('main')
    dp.include_router(handler_command)
    dp.include_router(handler_date_of_birthday)
    dp.include_router(handler_event_day)
    dp.include_router(handler_delete_event)
    dp.include_router(handler_change_date)
    dp.include_router(handler_calendar)
    dp.include_router(handler_with_hours)
    # await run_checking_notification()
    # await dp.start_polling(bot, on_shutdown=on_shutdown, skip_updates=True)
    await asyncio.gather(dp.start_polling(bot, on_shutdown=on_shutdown,
                                          skip_updates=True),run_checking_notification())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот был выключен')
