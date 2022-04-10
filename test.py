import psycopg2
from psycopg2 import Error
from config import db

try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user=db['user'],
                                  password=db['password'],
                                  host=db['host'],
                                  port=db['port'],
                                  database=db['database'])

    # Курсор для выполнения операций с базой данных
    cursor = connection.cursor()
    # Распечатать сведения о PostgreSQL
    print("Информация о сервере PostgreSQL")
    print(connection.get_dsn_parameters(), "\n")
    # Выполнение SQL-запроса
    cursor.execute("SELECT version();")
    # Получить результат
    record = cursor.fetchone()
    print("Вы подключены к - ", record, "\n")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")