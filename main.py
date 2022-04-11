import discord
from discord.ext import commands
import sqlite3
from config import settings, db


bot = commands.Bot(command_prefix=settings['prefix'], intents = discord.Intents.all())
print('Подключение к БД...')
db = sqlite3.connect('server.db')
curs = db.cursor()

@bot.event
async def on_ready():
    print("Бот включен\n ")
    print('Создание таблицы')
    curs.execute('''CREATE TABLE if NOT EXISTS users (
        id          int,
        username    varchar(80),
        firstname   varchar(80),
        middlename  varchar(80),
        surname     varchar(80),
        birthday    date
        );''')
    db.commit()
    for guild in bot.guilds:
        for member in guild.members:
            if curs.execute(f'SELECT id FROM users WHERE id = {member.id}').fetchone() is None and member != bot.user:
                curs.execute(f'INSERT INTO users ("id", "username") VALUES ("{member.id}", "{member}")')
                db.commit()
                await bot.get_channel(settings['regchan']).send(f'@{member}, пройдите регистрацию чтобы начать RP. Если готовы, напишите "Регистрация".')
                print(member)
            else:
                pass
    print('Всё готово к работе')

@bot.event
async def on_member_join(member):
    if curs.execute(f'SELECT id FROM users WHERE id = {member.id}').fetchone() is None:
        curs.execute(f'INSERT INTO users ("id", "username") VALUES ("{member.id}", "{member}")')
        db.commit()
        await bot.get_channel(settings['regchan']).send(f'@{member}, пройдите регистрацию чтобы начать RP. Если готовы, напишите "$reg".')
        print(member)
    else:
        pass

@bot.command() # Command to start registration
async def reg(ctx):
    print("создание комнаты")
    guild = ctx.message.guild
    member = ctx.author
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await guild.create_text_channel(f'регистрация {member}', overwrites = overwrites)
    await ctx.reply(f'Переходи в эту комнату: <#{channel.id}>')
    await bot.get_channel(channel.id).send('Приступим! Ты готов(-а)?')


@bot.event
async def on_message(msg):
    channel = msg.channel
    author = msg.author
    if author != bot.user:
        text = msg.content
        print(f'{author}: {text}')
#        if 'регистрация' in channel: Сегодня доделаю!

    
    await bot.process_commands(msg)


        

bot.run(settings['token'])