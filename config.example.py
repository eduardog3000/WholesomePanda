# All properties must be set, at least to None.

# Basic bot stuff
token = 'TOKEN'
prefix = '!'

# List of channel ids as int. Most commands will only work in these channels.
# See <bindings> and <global_bindings> below for overrides.
bound_channels = [123456789012345678, 987654321098765432]

# A list of roles able to use mod level bot commands.
# Can be the roles' exact names as strings or their ids as ints.
# Mods for the warn command can be defined separately below.
mod_roles = ['Mod', 123456789012345678]

# Whether the bot should respond to commands with a message. Default: True
msg_response = True
# Whether the bot should respond to commands with a reaction. Default: False
reaction_response = False
# Both can be true, the bot will respond with both.

"""
Colors for color change command.

<colors> is a list of the standard color roles.
Colors must exactly match the name of the corresponding role on your server.
If <colors> is falsy, the color change command will be disabled.

<emoji> is a list of emoji corresponding to the colors in <color>, for a nice response.
If <emoji> is falsy, the response won't include an emoji.
"""
colors = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple', 'Pink']
emoji = [':heart:', ':large_orange_diamond:', ':yellow_heart:', ':green_heart:', ':blue_heart:', ':purple_heart:', ':sparkling_heart:']

"""
Emoji reactions to certain words.

Should be a dict where the key is a regex string to match
    and the value is an emoji or server emoji code (e.g. <:wholesome:287391753781248010>) to respond with.

Example regex for a single word: r'\btree\b'. To allow plural it would be r'\btrees?\b'.
"""
reactions = {
    r'\bgays?\b': '🏳️‍🌈',
    r'\btrees?\b': '🌳',
    r'\bmoons?\b': '🌕',
    r'\bsuns?\b': '🌞',
    r'\blove\b': '❤',
    r'\bturtles?\b': '🐢',
    r'\bpizzas?\b': '🍕'
}

"""
Database
<db> is either a dict with properties for the logging, songs, and warnings modules,
    or False to disable all features that need a database.
"""
db = {
    # Config for message logging.
    # Either a dict with more properties, or False to disable logging.
    'logging': {
        # A channel or list of channels where messages shouldn't be logged.
        'excluded': [123456789012345678],
        # Whether the quote command should be enabled, which randomly quotes logged messages.
        'quote': True
    },
    # Whether song plays should be logged.
    'songs': True,
    # Config for warning system.
    # Either a dict with more properties, or False to disable warnings.
    'warnings': {
        # The channel warnings should be logged to.
        'log_channel': 123456789012345678,
        # A list of the roles that can warn
        # Can be the exact names of the roles as strings or their ids as ints.
        # 'mod_roles': mod_roles makes warn mods the exact same as bot mods.
        'mod_roles': mod_roles
    }
}

# Overrides to allow to disallow specific commands by channel.
# Should be an object whose properties are of this form:
# 'commandname_string': {
#    channel_int: True if enabled, False if disabled
# }
bindings = {
    'quote': {
        123456789012345678: True,
        987654321234567890: False
    }
}
# Commands that will work in every channel regardless of other settings.
# Overrides both the <bound_channels> and <bindings> settings for the listed commands.
# Should be a list of strings with the exact (primary) name of the commands.
global_bindings = ['hug', 'warn', 'warnings', 'wr', 'wc']
