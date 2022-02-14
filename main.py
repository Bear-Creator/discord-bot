import discord
from discord.ext import commands
from config import settings

bot = commands.Bot(command_prefix = settings['prefix'])

