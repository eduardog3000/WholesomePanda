"""
Otherwise good features that I decided not to finish.
"""

# chatbot.py
import operator

@commands.Cog.listener()
@checks.config(config.starboard)
async def on_reaction_add(self, reaction, user):
    props = operator.itemgetter('emoji', 'count')
    if props(reaction) == props(config.starboard):
        reaction.message.add_reaction(config.starboard['mark_emoji'])
        embed = discord.embed()

# config.py
"""
If a message recieves a lot of reactions, post it to a special channel.

<starboard> is either a dict with the properties below, or False to disable starboard.
<channel> is the id of the starboard channel as an int.
<count> is the number of reactions needed to star the message. Default: 5
<emoji> is the emoji that is counted. Default: '⭐'
<mark_emoji> is the emoji the bot should react with when <count> is reached. Default '🌟'
"""
starboard = {
    'channel': 1234567890,
    'count': 5,
    'emoji': '⭐',
    'mark_emoji': '🌟'
}