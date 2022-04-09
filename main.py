from discord.ext import commands
from config import settings 

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print("Everything's all ready to go~")
    

@bot.event
async def on_message(msg):
    author = msg.author
    if author != bot.user:
        text = msg.content
        print(f'{author}: {text}')
        await msg.reply('Я пока не работаю')



bot.run(settings['token'])