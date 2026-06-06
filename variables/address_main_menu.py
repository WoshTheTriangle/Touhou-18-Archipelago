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
ADDR_MENU_LOCATION_OFFSET = [0x18]

# Due to some weird assembly I don't know, changing this value forces the game into the main menu or stage.
# 4 - Main Menu
# 7 - Stage
ADDR_MENU_STATE = 0x000CCDF0+0x000007F8

# Since extra stage is the only spot with 1 option, we can find if we are entering the extra stage with this.
ADDR_SELECTION_OPTION_COUNT = 0x2c

ADDR_MENU_SELECT = [0x24]

'''
Scorefile offsets
'''
#1 byte indices

ADDR_SCOREFILE_CHARACTER_OFFSET = 0x8
ADDR_DIFFICULTIES_BEATEN_OFFSET = 0x64ec
ADDR_SCOREFILE_SHOTTYPE_SIZE = 0x130f0

# Beginning index of achievement array (up to +29)
ADDR_ACHIEVEMENT_OFFSET = [0x5f508]

# Beginning index of unlocked cards array (up to +35)
ADDR_UNLOCKED_CARD_OFFSET = [0x5f588]

ADDR_CARD_SLOTS_OFFSET = [0x5f678]