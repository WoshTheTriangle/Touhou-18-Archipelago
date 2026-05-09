'''
Variables: Addresses used in the main menu.
'''

# Add with the game's base address.
# Controls main menu information.
ADDR_MAIN_MENU_PTR = 0x000CF43C

# Controls unlocks
ADDR_SCOREFILE_PTR = 0x000CF41C

'''
Main menu offsets
'''
#1 - Main Menu
#5 - Difficulty Select
#6 - Character Select
#8 - Practice Stage Select
#18 - Spell Card Practice Stage Select, 19 is the card itself
ADDR_MENU_SPOT_OFFSET = [0x18]


'''
Scorefile offsets
'''
#1 byte indices

# Beginning index of achievement array (up to +29)
ADDR_ACHIEVEMENT_OFFSET = [0x5f508]

# Beginning index of unlocked cards array (up to +35)
ADDR_UNLOCKED_CARD_OFFSET = [0x5f588]