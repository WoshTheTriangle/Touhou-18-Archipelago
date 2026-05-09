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

ADDR_LIVES = 0x000CCD48
ADDR_BOMBS = 0x000CCD58 
ADDR_FUNDS = 0x000CCD34 
ADDR_POWER = 0x000CCD38 
ADDR_BOMB_PIECES = 0x000CCD5C 
ADDR_LIFE_PIECES = 0x000CCD4C 
ADDR_CURRENT_STAGE = 0x000CCCDC 


#Non-Static Addresses

'''
Enemy Manager Offsets
'''

# If a boss is active, this address will hold a non-zero value.
ADDR_BOSS_ID_OFFSET = [0x48]

'''
Card Manager Offsets
'''
# The cards are held in a linked list.
# The first value in the list holds some nonsense card so we start at the second card.
ADDR_CARD_LIST_HEAD_OFFSET = [0x1C, 0x0]

ADDR_NUM_CARDS_OFFSET = [0x28]

