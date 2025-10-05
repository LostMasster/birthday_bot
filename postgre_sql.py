import psycopg2
from psycopg2 import pool
from sql_info import user, password, database, host
from datetime import datetime


connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=user,
    password=password,
    host=host,
    database=database)

if connection_pool:
    print("Connection pool created successfully")


async def new_user(user_id, first_name, last_name, date_of_registration):
    conn = connection_pool.getconn()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO users (user_id, first_name, last_name, "
                           f"date_of_registration) VALUES (%s, %s, %s, %s) ON CONFLICT (user_id) DO NOTHING",
                       (user_id, first_name, last_name, date_of_registration))
            conn.commit()
            cursor.close()
            print(f"Пользователь {user_id} добавлен в базу данных.")
        except (Exception, psycopg2.DatabaseError) as error:
            print("Ошибка при работе с PostgreSQL", error)
        finally: connection_pool.putconn(conn)
    else: print("Не удалось подключиться к базе данных.")


def test_funk():
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        with connection.cursor() as cursor:
            user_id = 6555200949
            cursor.execute(
                'SELECT * from important_dates where user_id = %s' , (user_id,)
            )
            username = cursor.fetchall()
            print(f'----data_id----user_id----date_name----event_day----\n')
            for data_id, user_id, date_name, event_name in username:
                print(f'----{data_id}----{user_id}----{date_name}----{event_name}\n')
            connection.close()
            cursor.close()
            # for data_id, user_id, date_name, event_date in username:

                # print(f'{date_name}   {event_date}')
            # user_id = 6555200949
            # date_name = 'День рождения Артура Олеговича'
            # cursor.execute(
            #     'SELECT event_date FROM important_dates WHERE user_id = %s'
            #     ' AND date_name = %s', (user_id, date_name)
            # )
            # username = cursor.fetchone()[0]
            # print(username)
            # print(f'Server version {cursor.fetchall()}')
            # print(f'Server version {cursor.fetchone()}')
    except Exception as _ex:
        print('[INFO] Error while working with PostgreSQL', _ex)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')