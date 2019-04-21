import discord.ext.commands as commands

import config as cfg

def config(config_prop):
    def predicate(ctx):
        return config_prop
    return commands.check(predicate)

def quote_enabled():
    def predicate(ctx):
        return cfg.db['logging'] and cfg.db['logging']['quote']
    return commands.check(predicate)
    
def in_bound_channel():
    def predicate(ctx):
        command = ctx.command.name
        if command in cfg.global_bindings: return True
        channel = ctx.channel.id
        if command in cfg.bindings and channel in cfg.bindings[command]:
            return cfg.bindings[command]
        else:
            return channel in cfg.bound_channels
    return commands.check(predicate)

def not_in_channel(*channels):
    def predicate(ctx):
        return ctx.channel.id not in channels
    return commands.check(predicate)
