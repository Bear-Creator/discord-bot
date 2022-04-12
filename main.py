import discord
from discord.ext import commands
import sqlite3
from config import settings, db



def registration():
    da = 1

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
                await bot.get_channel(settings['regchan']).send(f'<@{member.id}>, пройдите регистрацию чтобы начать RP. Если готовы, напишите "$reg".')
                print(f'{member} добавлен в базу')
            else:
                pass
    print('Всё готово к работе')

@bot.event
async def on_member_join(member):
    if curs.execute(f'SELECT id FROM users WHERE id = {member.id}').fetchone() is None:
        curs.execute(f'INSERT INTO users ("id", "username") VALUES ("{member.id}", "{member}")')
        db.commit()
        await bot.get_channel(settings['regchan']).send(f'<@{member.id}>, пройдите регистрацию чтобы начать RP. Если готовы, напишите "$reg".')
        print(f'{member} добавлен в базу')
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
    await bot.get_channel(channel.id).send('Приступим!')
    await bot.get_channel(channel.id).send('Придумай легенду своего пресонажа')
    await bot.get_channel(channel.id).send('Напишите имя персонажа')
    

@bot.command() #Delete user info
async def deluser(cxt, a: int):
    user = curs.execute(f'SELECT username FROM users WHERE id = {a};').fetchone()
    curs.execute(f'DELETE FROM users WHERE id = {a};')
    db.commit() 
    print(f'Пользователь {user} удалён из базы')
    await cxt.reply(f'Пользователь {user} удалён из базы')


@bot.event
async def on_message(msg):
    channel = msg.channel
    author = msg.author
    if author != bot.user:
        text = msg.content
        print(f'{author}: {text}')
        if 'регистрация' in channel:
            info = ('firstname', 'middlename', 'surname', 'birthday')
            data = curs.execute(f'SELECT firstname, middlename, surname, birthday FROM users WHERE id = {msg.author.id}').fetchone()
            usrdt = dict(zip(info, data))
            if usrdt['firstname'] == None:
                back = 'firstname'
                answer = 'Теперь отчество'
            elif usrdt['middlename'] == None:
                back = 'middlename'
                answer = 'Фамилию...'
            elif usrdt['surname'] == None:
                back = 'surname'
                answer = '...и дату рождения в формате ГГГГ-ММ-ДД (Например: 1950-10-29)'
            elif usrdt['birthday'] == None:
                back = 'birthday'
                answer = 'Всё! Вы зарегистрированы! Удачного RP, Товарищ!'
            else:
                a = 1

    
    await bot.process_commands(msg)


bot.run(settings['token'])