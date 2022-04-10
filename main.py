from discord.ext import commands
import psycopg2
from psycopg2 import Error
from config import settings, db

bot = commands.Bot(command_prefix=settings['prefix'])

try:
    # Подключение к существующей базе данных
    db = psycopg2.connect(user=db['user'],
                          password=db['password'],
                          host=db['host'],
                          port=db['port'],
                          database=db['database'])

    #Курсор для выполнения операций с базой данных
    curs = db.cursor()

    # Распечатать сведения о PostgreSQL
    print("Информация о сервере PostgreSQL")
    print(db.get_dsn_parameters(), "\n")

    # Выполнение SQL-запроса
    curs.execute("SELECT version();")

    # Получить результат
    print("Вы подключены к - ", curs.fetchone(), "\n")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)


@bot.event
async def on_ready():
    print("Бот включен\n ")
    
    global db, curs
    


@bot.event
async def on_message(msg):
    author = msg.author
    if author != bot.user:
        text = msg.content
        print(f'{author}: {text}')
        



bot.run(settings['token'])
