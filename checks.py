import discord.ext.commands as commands

import config as cfg

def config(config_prop):
    def predicate(ctx):
        return config_prop
    return commands.check(predicate)

def quote_enabled():
    def predicate(ctx):
        return config.db['logging'] and config.db['logging']['quote']
    return commands.check(predicate)
    
def in_bound_channel():
    def predicate(ctx):
        return ctx.channel.id in cfg.bound_channels
    return commands.check(predicate)