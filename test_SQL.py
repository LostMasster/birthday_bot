import psycopg2
from psycopg2 import pool
from sql_info import user, password, database, host


connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    user=user,
    password=password,
    host=host,
    database=database
)

async def test_func():
    if connection_pool:
        print("Connection pool created successfully")

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
            data_id = '2025-01-06 20:19:42'
            new_event_date = '31.01.2025'
            cursor.execute(
                'UPDATE important_dates SET event_date = %s WHERE user_id = %s AND data_id = %s'
                , (new_event_date, user_id, data_id)
            )
            connection.commit()
            cursor.close()
    except Exception as _ex:
        print('[INFO] Error while working with PostgreSQL', _ex)
    finally:
        if connection:
            connection.close()
            print('[INFO] PostgreSQL connection closed')

num_list = [[1], [2], [3], [4]]
for _ in num_list:
    print(_[0])