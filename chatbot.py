import inspect
import operator
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

		if config.colors:
			bot.help_command = ColorHelpCommand()

		if config.db:
			if not os.path.isfile('panda.db') and os.path.isfile('panda.example.db'):
				import shutil
				shutil.copy2('panda.example.db', 'panda.db')

			dbexists = os.path.isfile('panda.db')

			self.conn = sqlite3.connect('panda.db', detect_types=sqlite3.PARSE_DECLTYPES)
			self.cur = self.conn.cursor()

			if not dbexists:
				self.conn = sqlite3.connect('panda.db', detect_types=sqlite3.PARSE_DECLTYPES)
				self.cur = self.conn.cursor()
				self.cur.execute('''CREATE TABLE logs 
					(id INTEGER PRIMARY KEY, guild INT, channel INT, author INT, timestamp TIMESTAMP, message TEXT, is_edited BOOLEAN DEFAULT 0, is_deleted BOOLEAN DEFAULT 0)''')
				self.cur.execute('''CREATE TABLE warnings
					(id INTEGER PRIMARY KEY AUTOINCREMENT, warned INT, mod INT, reason TEXT, timestamp TIMESTAMP)''')
				self.cur.execute('''CREATE TABLE songs
					(filename TEXT PRIMARY KEY, url TEXT, ytid TEXT, title TEXT, plays INT DEFAULT 0)''')
				self.conn.commit()
		else:
			config.db = {'logging': False, 'songs': False, 'warnings': False}
	
	@commands.group(aliases=['colour', 'c'], invoke_without_command=True)
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
		await ctx.trigger_typing()
		color_roles = [r for r in ctx.guild.roles if r.name in config.colors]
		await ctx.author.remove_roles(*color_roles, reason='User requested colors cleared.')
		emoji = ':black_heart: ' if config.emoji else ''
		await self.respond(ctx, f'{emoji}Color cleared.', [':white_check_mark:', emoji])
	
	@color.command(name='help')
	@checks.in_bound_channel()
	@checks.config(config.colors)
	async def color_help(self, ctx):
		"""Shows available colors."""
		await ctx.send('Available colors are '
			f'{", ".join(config.colors[:-1])}, and {config.colors[-1]}.\n'
			f'To clear your colors use `{config.prefix}color clear`.')

	@commands.command()
	async def hug(self, ctx, to_hug):
		"""Hug someone, it's nice."""
		await ctx.send(f':hugging: | {ctx.author} hugged {to_hug} with all the love :heart:')

	@commands.command()
	@checks.config(config.db['logging'])
	@checks.config(config.db['logging']['quote'])
	async def quote(self, ctx, user: typing.Optional[discord.Member]):
		"""Randomly quotes the given user."""
		user = user or ctx.author
		self.cur.execute('SELECT message, timestamp FROM logs WHERE author = ? AND is_deleted != 1 ORDER BY RANDOM() LIMIT 1', (user.id,))
		result = self.cur.fetchone()
		await ctx.send(embed=discord.Embed(description=result[0], timestamp=result[1])
			.set_author(name=user.display_name, icon_url=user.avatar_url_as(static_format='png')) # iOS doesn't support webp...
			.set_footer(text=f'@{user.name}#{user.discriminator}'))
	
	@commands.group(aliases=['w', 'warns'], invoke_without_command=True)
	@checks.config(config.db['warnings'])
	@commands.has_any_role(*config.db['warnings']['mod_roles'])
	async def warn(self, ctx, user: discord.User, *, reason):
		"""Warns the mentioned user with the given reason."""
		self.cur.execute('''INSERT INTO warnings (warned, mod, reason, timestamp) VALUES (?,?,?,?)''',
			(user.id, ctx.author.id, reason, ctx.message.created_at))
		self.conn.commit()
		await user.send(f'You have been warned by {ctx.author.mention} for `{reason}`.')
		await self.bot.get_channel(config.db['warnings']['log_channel']).send(embed=discord.Embed()
			.set_author(name='Warning', icon_url=user.avatar_url or user.default_avatar_url)
			.add_field(name='User', value=user.mention, inline=False)
			.add_field(name='Moderator', value=ctx.author.mention, inline=False)
			.add_field(name='Reason', value=reason, inline=False))
	
	@warn.command(name='show', aliases=['s', 'ing', 'ings'])
	@checks.config(config.db['warnings'])
	@commands.has_any_role(*config.db['warnings']['mod_roles'])
	async def warn_show(self, ctx, user_or_warning_id: typing.Union[discord.User, int]):
		"""Shows all warnings the mentioned user has.
		Or shows the full info for a warning given its id."""

		if isinstance(user_or_warning_id, discord.User):
			user = user_or_warning_id
			self.cur.execute('SELECT id, mod, reason, timestamp FROM warnings WHERE warned = ?', (user.id,))
			timestamp = moderator = reason = ''
			warnings = 0
			for result in self.cur.fetchall():
				timestamp += f'`{str(result[0]).zfill(3)}`  {result[3]}\n'
				mod = ctx.guild.get_member(result[1])
				moderator += f'{mod.name}#{mod.discriminator}\n'
				rea = result[2]
				reason += (rea if len(rea) <= 20 else rea[:16] + '...') + '\n'
				warnings += 1
			
			await ctx.send(embed=discord.Embed(title=f'{warnings} Warnings')
				.set_author(name=f'{user.name}#{user.discriminator} ({user.id})',
					icon_url=user.avatar_url_as(static_format='png'))
				.add_field(name='#  Timestamp', value=timestamp)
				.add_field(name='Moderator', value=moderator)
				.add_field(name='Reason', value=reason)
				.set_footer(text=f'Use `{config.prefix}{ctx.invoked_with} <id>` to see the full reason for a specific warning.'))
		else:
			id = user_or_warning_id
			self.cur.execute('SELECT warned, mod, reason, timestamp FROM warnings WHERE id = ?', (id,))
			result = self.cur.fetchone()
			user = ctx.guild.get_member(result[0])
			mod = ctx.guild.get_member(result[1])

			await ctx.send(discord.Embed(title=f'Warning {id}')
				.set_author(name=f'{user.name}#{user.discriminator} ({user.id})',
					icon_url=user.avatar_url or user.default_avatar_url)
				.add_field(name='Timestamp', value=result[3], inline=False)
				.add_field(name='Moderator', value=f'{mod.name}#{mod.discriminator}\n', inline=False)
				.add_field(name='Reason', value=result[2], inline=False))
	
	@commands.command(name='warnings', aliases=['ws', 'warning', 'wing', 'wings'], hidden=True)
	async def warn_show_short(self, ctx, user_or_warning_id: typing.Union[discord.User, int]):
		"""Shortcut for warn show.
		Shows all warnings the mentioned user has.
		Or shows the full info for a warning given its id."""
		await ctx.invoke(self.warn_show, user_or_warning_id)
	
	@warn.command(name='remove', aliases=['r'])
	@checks.config(config.db['warnings'])
	@commands.has_any_role(*config.db['warnings']['mod_roles'])
	async def warn_remove(self, ctx, warning_id: int):
		"""Removes a warning by its id."""
		self.cur.execute('DELETE FROM warnings WHERE id = ?', (warning_id,))
		self.conn.commit()
		await ctx.send('***Warning removed.***')
	
	@commands.command(name='wr', hidden=True)
	async def warn_remove_short(self, ctx, warning_id: int):
		"""Shortcut for warn remove.
		Removes a warning by its id."""
		await ctx.invoke(self.warn_remove, warning_id)
	
	@warn.command(name='clear', aliases=['c'])
	@checks.config(config.db['warnings'])
	@commands.has_any_role(*config.db['warnings']['mod_roles'])
	async def warn_clear(self, ctx, user: discord.User):
		"""Removes all warnings from the mentioned user."""
		self.cur.execute('DELETE FROM warnings WHERE warned = ?', (user.id,))
		self.conn.commit()
		await ctx.send(f'***Warnings cleared for {user.mention}.***')

	@commands.command(name='wc', hidden=True)
	async def warn_clear_short(self, ctx, user: discord.User):
		"""Shortcut for warn clear.
		Removes all warnings from the mentioned user."""
		await ctx.invoke(self.warn_clear, user)

	@commands.Cog.listener(name='on_message')
	@checks.config(config.db['logging'])
	@checks.not_in_channel(config.db['logging']['excluded'])
	async def log_message(self, message):
		self.cur.execute('INSERT INTO logs VALUES (?,?,?,?,?,?,0,0)',
			(message.id, message.guild.id, message.channel.id, message.author.id, message.created_at, message.content))
		self.conn.commit()
	
	@commands.Cog.listener(name='on_message')
	@commands.bot_has_permissions(add_reactions=True)
	@checks.not_in_channel(config.dont_react_in)
	async def keyword_react(self, message):
		for key in config.reactions:
			if re.match(key, message.content, re.IGNORECASE):
				await self.add_reaction(message, config.reactions[key])

	@commands.Cog.listener()
	@checks.config(config.db['logging'])
	async def on_delete(self, message):
		self.cur.execute('UPDATE logs SET is_deleted = 1 WHERE message = ?', (message.id,))
		self.cur.commit()

	@commands.Cog.listener()
	async def on_command_error(self, ctx, err):
		print(err)
		if isinstance(err, commands.UserInputError):
			await ctx.send(inspect.cleandoc(f'''Input error for `{config.prefix}{ctx.command}`:
				```{err}```
				Showing help for `{config.prefix}{ctx.command}`:'''))
			await ctx.send_help(ctx.command)

	async def respond(self, ctx, message='', *reactions):
		if config.msg_response and message:
			await ctx.send(message)

		if config.reaction_response and self.has_permission(ctx, 'add_reactions'):
			for reaction in [r for r in reactions if r]:
				await self.add_reaction(ctx, reaction)
	
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

class ColorHelpCommand(commands.DefaultHelpCommand):
	async def add_command_formatting(self, command):
		help = command.help
		if command.name == 'color':
			command.help += f'\n\nAvailable colors are {", ".join(config.colors[:-1])}, and {config.colors[-1]}.'
		await super().add_command_formatting(command)
		command.help = help
