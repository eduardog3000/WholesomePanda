# All properties must be set, at least to None.

# Basic bot stuff
token = 'TOKEN'
prefix = '!'

# List of channel ids as int. Most commands will only work in these channels.
bound_channels = [123456789012345678, 987654321098765432]

# Whether the bot should respond to commands with a message (True) or just reactions (False)
msg_response = True

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

db = {
    'logging': {
        'excluded': [123456789012345678],
        'quote': True
    },
    'songs': True,
    'warnings': {
        'log_channel': 123456789012345678
    }
}