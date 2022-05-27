from sys import prefix
import time
import discord
from discord.ext import commands
import sqlite3
from config import settings



global db
global curs
print('Подключение к БД...')
db = sqlite3.connect('server.db')
curs = db.cursor()
prefix = settings['prefix']
bot = commands.Bot(command_prefix=prefix, intents = discord.Intents.all())

# Turning bot on/Adding all users in DB
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
                await bot.get_channel(settings['regchan']).send(f'<@{member.id}>, пройдите регистрацию чтобы начать RP. Если готовы, напишите "{prefix}reg".')
                print(f'{member} добавлен в базу')
            else:
                pass
    print('Всё готово к работе')

# Adding new users in DB
@bot.event
async def on_member_join(member):
    if curs.execute(f'SELECT id FROM users WHERE id = {member.id}').fetchone() is None:
        curs.execute(f'INSERT INTO users ("id", "username") VALUES ("{member.id}", "{member}")')
        db.commit()
        await bot.get_channel(settings['regchan']).send(f'<@{member.id}>, пройдите регистрацию чтобы начать RP. Если готовы, напишите "$reg".')
        print(f'{member} добавлен в базу')
    else:
        pass

async def update_userinf(member: discord.Member):

    usr = curs.execute(f'SELECT * FROM users WHERE id = {str(member.id)}').fetchone()
    if usr[5] != None:
        fname = usr[2]
        surname = usr[4]
        nick = usr[1][:-5]

        name = fname
        if len(name + surname) <=31:
            name += ' ' + surname
        if len(name + nick) <= 29:
            name += ' (' + nick + ')'
        await member.edit(nick=f'{name}')
    return



# Command to start registration
@bot.command() 
async def reg(ctx):
    print("создание комнаты")
    guild = ctx.message.guild
    member = ctx.author
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
    }
    channel = await guild.create_text_channel(f'регистрация {member}', overwrites = overwrites)
    print(channel)
    send = bot.get_channel(channel.id)
    await ctx.reply(f'Переходи в эту комнату: <#{channel.id}>')
    await send.send('Приступим!')
    await send.send('Придумай легенду своего пресонажа')
    await send.send('Напишите имя персонажа')

#Delete user info
@bot.command() 
async def delinfo(cxt):
    user = cxt.author
    name =  curs.execute(f'SELECT username FROM users WHERE id = {user.id}').fetchone()
    await user.edit(nick = name)

    curs.execute(f'DELETE FROM users WHERE id = {user.id};')
    db.commit()
    print(f'Пользователь {user} удалён из базы')
    await cxt.reply(f'Пользователь {user} удалён из базы')

    curs.execute(f'INSERT INTO users ("id", "username") VALUES ("{user.id}", "{user}")')
    db.commit()
    await bot.get_channel(settings['regchan']).send(f'<@{user.id}>, пройдите регистрацию чтобы начать RP. Если готовы, напишите "$reg".')
    print(f'{user} добавлен в базу')

# On message
@bot.event
async def on_message(msg):
    channel = msg.channel
    author = msg.author
    if author == bot.user:
        return
    text = msg.content

    print(f'{author}: {text}')


    #message in registration channel
    if 'регистрация' in str(channel):
        send_to = bot.get_channel(channel.id)

        info = ('firstname', 'middlename', 'surname', 'birthday')
        data = curs.execute(f'SELECT firstname, middlename, surname, birthday FROM users WHERE id = {msg.author.id}').fetchone()
        usrdt = dict(zip(info, data))

        if usrdt['firstname'] == None:
            back = 'firstname'
            await send_to.send('Хорошо, теперь отчество')

        elif usrdt['middlename'] == None:
            back = 'middlename'
            await send_to.send('Фамилию...')

        elif usrdt['surname'] == None:
            back = 'surname'
            await send_to.send('...и дату рождения в формате ГГГГ-ММ-ДД (Например: 1950-10-29)')

        elif usrdt['birthday'] == None:
            back = 'birthday'
            await send_to.send('Всё! Вы зарегистрированы! Удачного RP, Товарищ!')
            time.sleep(5)

            if channel:
                await channel.delete()

        else:
            back = False
            await send_to.send("Вы уже зарегистрированы!")
            time.sleep(5)

            if channel:
                await channel.delete()
            
        if back:
            print(f'Ввожу {back}')
            curs.execute(f'UPDATE users SET {back} = "{text}" WHERE id = {author.id}')
            db.commit()

        await update_userinf(author)



    await bot.process_commands(msg)


bot.run(settings['token'])