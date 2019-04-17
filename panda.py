import logging

import discord.ext.commands as commands

import config
import checks

# Setup logging
"""
rlog = logging.getLogger()
rlog.setLevel(logging.INFO)
handler = logging.FileHandler('panda.log', encoding='utf-8')
handler.setFormatter(logging.Formatter('{asctime}:{levelname}:{name}:{message}', style='{'))
rlog.addHandler(handler)
"""

# Complicated bot creation
bot = commands.Bot(config.prefix)
# bot.load_extension('music')
bot.load_extension('chatbot')

# For when the bot is shitting itself
@bot.command()
@commands.has_permissions(manage_guild=True)
async def reload(ctx):
	"""Reloads all modules.

	This command requires the Manage Server permission.
	"""
	# ctx.bot.unload_extension('music')
	ctx.bot.unload_extension('chatbot')
	# ctx.bot.load_extension('music')
	ctx.bot.load_extension('chatbot')
	await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

# For when the bot is really shitting itself
@bot.command()
@commands.has_permissions(manage_guild=True)
async def restart(ctx):
	await ctx.bot.close()
	await ctx.bot.run(config.token)

# For when the bot is REALLY shitting itself
@bot.command()
@commands.has_permissions(manage_guild=True)
async def shutdown(ctx):
	await ctx.bot.close()

# @bot.listen()
# async def on_command_error(ctx, e):
# 	await ctx.message.add_reaction('\N{CROSS MARK}')
# 	await ctx.send(e)

# Let's rock ! (and roll, because panda are round and fluffy)
bot.run(config.token)
