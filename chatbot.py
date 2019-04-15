import inspect
import os
import re
import sqlite3

import discord
import discord.ext.commands as commands

import config
import checks

def setup(bot):
	bot.add_cog(ChatBot(bot))

class ChatBot(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		if config.db:
			if not os.path.isfile('panda.db') and os.path.isfile('panda.example.db'):
				import shutil
				shutil.copy2('panda.example.db', 'panda.db')
			
			conn = sqlite3.connect('panda.db', detect_types=sqlite3.PARSE_DECLTYPES)
			cur = conn.cursor()

			if not os.path.isfile('panda.db'):
				cur = conn.cursor()
				cur.execute('''CREATE TABLE logs 
					(id INT PRIMARY KEY, guild INT, channel INT, author INT, timestamp TIMESTAMP, message TEXT, is_edited BOOLEAN DEFAULT 0)''')
				cur.execute('''CREATE TABLE warnings
					(id INT PRIMARY KEY AUTOINCREMENT, warned INT, mod INT, message TEXT, timestamp TIMESTAMP)''')
				cur.execute('''CREATE TABLE songs
					(filename TEXT PRIMARY KEY, url TEXT, ytid TEXT, title TEXT, plays INT DEFAULT 0''')
				conn.commit()
			
			self.conn = conn
			self.cur = cur
		else:
			config.db = {'logging': False, 'songs': False, 'warnings': False}
	
	@commands.group(aliases=['colour'], invoke_without_command=True)
	@commands.bot_has_permissions(manage_roles=True)
	@checks.in_bound_channel()
	@checks.config(config.colors)
	async def color(self, ctx, color):
		"""Changes your color role to the specified color."""
		await ctx.trigger_typing()
		color = color.lower()
		color_roles = [r for r in ctx.guild.roles if r.name in config.colors]
		color_r = next((r for r in color_roles if r.name.lower() == color), None)
		
		if color_r:
			await ctx.author.remove_roles(*color_roles, reason='User requested color change.')
			await ctx.author.add_roles(color_r, reason='User requested color change.')
			emoji = config.emoji[config.colors.index(color_r.name)] + ' ' if config.emoji else ''
			await self.respond(ctx, f'{emoji}Color set to {color}.', [':white_check_mark:', emoji[:-1]])
		else:
			raise commands.CommandError(f'Color not available. Available colors are '
				f'{", ".join(config.colors[:-1])}, and {config.colors[-1]}.\n'
				f'To clear your colors use `{config.prefix}color clear`.')
	
	@color.command(name='clear', aliases=['none', 'reset'])
	@checks.in_bound_channel()
	@checks.config(config.colors)
	async def color_clear(self, ctx):
		"""Removes any color role you have."""
		color_roles = [r for r in ctx.guild.roles if r.name in config.colors]
		await ctx.author.remove_roles(*color_roles, reason='User requested colors cleared.')
		emoji = ':black_heart: ' if config.emoji else ''
		await self.respond(ctx, f'{emoji}Color cleared.', [':white_check_mark:', ':black_heart:'])
	
	@color.command(name='help')
	@checks.in_bound_channel()
	@checks.config(config.colors)
	async def color_help(self, ctx):
		"""Shows available colors."""
		await ctx.send('Available colors are '
			f'{", ".join(config.colors[:-1])}, and {config.colors[-1]}.\n'
			f'To clear your colors use `{config.prefix}color clear`.')

	@commands.command()
	async def hug(self, ctx, author, to_hug):
		"""Hug someone, it's nice."""
		await ctx.trigger_typing()
		await ctx.send(f':hugging: | {author} hugged {to_hug} with all the love :heart:')
	
	@commands.group(aliases=['w'], invoke_without_command=True)
	@commands.has_permissions()
	@checks.config(config.db['warnings'])
	async def warn(self, ctx, user: discord.User, *, reason):
		"""Warns the mentioned user with the given reason."""
		pass
	
	@warn.command(name='show', aliases=['s', 'ings'])
	async def warn_show(self, ctx, user: discord.User):
		"""Shows all warnings the mentioned user has."""
		print('warn_show')
		pass
	
	@commands.command(name='warnings', aliases=['ws', 'wings'], hidden=True)
	async def warn_show_short(self, ctx, user: discord.User):
		await ctx.invoke(self.warn_show, user)
	
	@warn.command(name='remove', aliases=['r'])
	async def warn_remove(self, ctx, warning_id: int):
		"""Removes a warning by its id."""
		pass
	
	@commands.command(name='wr', hidden=True)
	async def warn_remove_short(self, ctx, warning_id: int):
		await ctx.invoke(self.warn_remove, warning_id)
	
	@warn.command(name='clear', aliases=['c'])
	async def warn_clear(self, ctx, user: discord.User):
		"""Removes all warnings from the mentioned user."""
		pass

	@commands.command(name='wc', hidden=True)
	async def warn_clear_short(self, ctx, user: discord.User):
		await ctx.invoke(self.warn_clear, user)

	@commands.command()
	@checks.in_bound_channel()
	async def noimp(self, ctx):
		await ctx.send('Commands not yet implemented:\n```quote```')
	
	@commands.Cog.listener()
	async def on_message(self, message):
		print('on message')
		if config.db['logging'] and message.channel not in config.db['logging']['excluded']:
			self.cur.execute('''INSERT INTO logs VALUES (?,?,?,?,?,?)''',
				(message.id, messsage.guild.id, message.channel.id, message.author.id, message.created_at))

		if message.author is self.bot.user:
			return
		
		if self.has_permission(message, 'add_reactions'):
			for key in config.reactions:
				if re.match(key, message.content):
					await self.add_reaction(ctx, config.reactions[key])
	
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.errors.CheckFailure):
			return

	async def respond(self, ctx, message='', reactions=[]):
		if config.msg_response:
			await ctx.send(message)
		elif self.has_permission(ctx, 'add_reactions'):
			if type(reactions) is list:
				for reaction in [r for r in reactions if r]:
					await self.add_reaction(ctx, reaction)
			else:
				await self.add_reaction(ctx, reactions)
	
	async def add_reaction(self, ctx, reaction):
		if type(ctx) is discord.Context:
			ctx = ctx.message

		if type(reaction) is int:
			await ctx.add_reaction(self.bot.get_emoji(reaction))
		else:
			await ctx.add_reaction(reaction)
	
	def has_permission(self, ctx, permission):
		if type(ctx) in [discord.Message, commands.Context]:
			ctx = ctx.channel
		
		return getattr(self.bot.user.permissions_in(ctx), permission)