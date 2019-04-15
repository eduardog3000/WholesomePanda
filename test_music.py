import random

import discord

import discord.ext.commands as commands

def setup(bot):
    bot.add_cog(Music(bot))

class RandomAudio(discord.AudioSource):
    def read(self):
        print('read')
        return random.getrandbits(30720) | 0b11111111

class Music:
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def summon(self, ctx, *, channel: discord.VoiceChannel = None):
        if channel is None and not ctx.author.voice:
            raise commands.CommandError('You are not in a voice channel.')
        
        channel = channel or ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def play(self, ctx, song):
        ctx.voice_client.play(discord.PCMAudio(f'music/{song}'))
        await ctx.send(ctx.voice_client.is_playing())
    
    @commands.command()
    async def is_playing(self, ctx):
        await ctx.send(ctx.voice_client.is_playing())