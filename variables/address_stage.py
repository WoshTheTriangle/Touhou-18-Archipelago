'''
Variables: Addresses used in stages.
'''

# Static Addresses
# Should be added with the base game address.

ADDR_CARD_MANAGER_PTR = 0x000CF298
# Controls cards held by the player.

ADDR_ENEMY_MANAGER_PTR = 0x000CF2D0
# Used for finding whether a boss is active
# along with whether the player is in a stage.

ADDR_GUI_PTR = 0x000CF2E0
# GUI-related elements such as lives owned.

ADDR_PLAYER_PTR = 0x000CF410

ADDR_TIME_IN_STAGE = 0x000CCCE8

ADDR_NONFOCUS_SPEED_OFFSET = [0x477B4]
ADDR_FOCUS_SPEED_OFFSET = [0x477B8]
ADDR_NONFOCUS_DIAG_SPEED_OFFSET = [0x477BC]
ADDR_FOCUS_DIAG_SPEED_OFFSET = [0x477C0]

ADDR_LIVES = 0x000CCD48
ADDR_BOMBS = 0x000CCD58 
ADDR_FUNDS = 0x000CCD34 
ADDR_POWER = 0x000CCD38 
ADDR_BOMB_FRAGS = 0x000CCD5C 
ADDR_LIFE_FRAGS = 0x000CCD4C 
ADDR_CURRENT_STAGE = 0x000CCCDC 
ADDR_SCORE = 0x000CCCFC
ADDR_DIFFICULTY = 0x000CCD00
ADDR_CONTINUES = 0x000CCCD0
ADDR_POWER = 0x000CCD38

ADDR_CURRENT_CHARACTER = 0x000CCCF4

ADDR_LIFE_GUI_ELEMENT_OFFSET_HEAD = 0x4C
ADDR_BOMB_GUI_ELEMENT_OFFSET_HEAD = 0x68
ADDR_GUI_STATE_OFFSET = 0x494

GUI_ACTIVE = 2
GUI_UNACTIVE = 3

#Non-Static Addresses

'''
Enemy Manager Offsets
'''

# If a boss is active, this address will hold a non-zero value.
ADDR_BOSS_ID_OFFSET = [0x48]

ADDR_PLAYER_STATE_OFFSET = [0x476AC]

'''
Card Manager Offsets
'''
# The cards are held in a linked list.
# The first value in the list holds some nonsense card so we start at the second card.
ADDR_CARD_LIST_HEAD_OFFSET = [0x1C, 0x0]

ADDR_NUM_CARDS_OFFSET = [0x28]

