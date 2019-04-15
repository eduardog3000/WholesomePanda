import inspect
import os
import re
import sqlite3
import typing

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
					(id INT PRIMARY KEY AUTOINCREMENT, warned INT, mod INT, reason TEXT, timestamp TIMESTAMP)''')
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
	
	@commands.group(aliases=['w', 'warns'], invoke_without_command=True)
	@commands.has_permissions()
	@checks.config(config.db['warnings'])
	async def warn(self, ctx, author, user: discord.User, *, reason):
		"""Warns the mentioned user with the given reason."""
		self.cur.execute('INSERT INTO warnings (?,?,?,?)', (user.id, author.id, reason, ctx.message.created_at))
		self.conn.commit()
		await user.send(f'You have been warned by {author.mention} for `{reason}`.')
		embed = discord.Embed(title='')
		embed.set_author(name='Warning', icon_url=user.avatar_url or user.default_avatar_url)
		embed.add_field(name='User', value=user.mention, inline=False)
		embed.add_field(name='Moderator', value=author.mention, inline=False)
		await self.bot.get_channel(config.db['warnings']['log_channel']).send(embed=embed)
	
	@warn.command(name='show', aliases=['s', 'ing', 'ings'])
	async def warn_show(self, ctx, user_or_warning_id: typing.Union[discord.User, int]):
		"""Shows all warnings the mentioned user has.
		Or shows the full info for a warning given its id."""

		if isinstance(user_or_warning_id, discord.User):
			user = user_or_warning_id
			self.cur.execute('SELECT * FROM warnings WHERE user = ?', user.id)
			timestamp = moderator = reason = ''
			warnings = 0
			for result in self.cur.fetchall():
				timestamp += f'`{str(result["id"]).zfill(3)}`  {result["timestamp"]}\n'
				mod = ctx.guild.get_member(result['mod'])
				moderator += f'{mod.name}#{mod.discriminator}\n'
				rea = result['reason']
				reason += (rea if len(rea) <= 20 else rea[:16] + '...') + '\n'
				warnings += 1
			
			embed = discord.Embed(title=f'{warnings} Warnings')
			embed.set_author(name=f'{user.name}#{user.discriminator} ({user.id})', icon_url=user.avatar_url or user.default_avatar_url)
			embed.add_field(name='#  Timestamp', value=timestamp)
			embed.add_field(name='Moderator', value=moderator)
			embed.add_field(name='Reason', value=reason)
			embed.set_footer(text=f'Use `{config.prefix}warning <id>` to see the full reason for a specific warning.')
		else:
			id = user_or_warning_id
			self.cur.execute('SELECT * FROM warnings WHERE id = ?', id)
			result = self.cur.fetchone()
			user = ctx.guild.get_member(result['warned'])
			mod = ctx.guild.get_member(result['mod'])

			embed = discord.Embed(title=f'Warning {id}')
			embed.set_author(name=f'{user.name}#{user.discriminator} ({user.id})', icon_url=user.avatar_url or user.default_avatar_url)
			embed.add_field(name='Timestamp', value=result['timestamp'], inline=False)
			embed.add_field(name='Moderator', value=f'{mod.name}#{mod.discriminator}\n', inline=False)
			embed.add_field(name='Reason', value=result['reason'], inline=False)
		
		await ctx.send(embed=embed)
	
	@commands.command(name='warnings', aliases=['ws', 'warning', 'wing', 'wings'], hidden=True)
	async def warn_show_short(self, ctx, user_or_warning_id: typing.Union[discord.User, int]):
		await ctx.invoke(self.warn_show, user_or_warning_id)
	
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
		await ctx.send('Commands not yet implemented:\n`quote` and `warn [show|remove|clear]`')
	
	@commands.Cog.listener()
	async def on_message(self, message):
		if config.db['logging'] and message.channel not in config.db['logging']['excluded']:
			self.cur.execute('''INSERT INTO logs VALUES (?,?,?,?,?,?)''',
				(message.id, message.guild.id, message.channel.id, message.author.id, message.created_at))

		if message.author is self.bot.user:
			return
		
		if self.has_permission(message, 'add_reactions'):
			for key in config.reactions:
				if re.match(key, message.content):
					await self.add_reaction(message, config.reactions[key])

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
		if type(ctx) is commands.Context:
			ctx = ctx.message

		if type(reaction) is int:
			await ctx.add_reaction(self.bot.get_emoji(reaction))
		else:
			await ctx.add_reaction(reaction)
	
	def has_permission(self, ctx, permission):
		if type(ctx) in [discord.Message, commands.Context]:
			ctx = ctx.channel
		
		return getattr(self.bot.user.permissions_in(ctx), permission)