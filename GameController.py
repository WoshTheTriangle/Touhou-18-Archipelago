import pymem
import pymem.exception
import math

from .Tools import *
from .variables.address_main_menu import *
from .variables.address_shop import *
from .variables.address_stage import *
from .variables.address_cards import *
from .variables.stage_constants import *
from .variables.card_constants import *
from .variables.meta_data import *




class GameController:
    '''Memory accessing class'''

    def __init__(self):
        
        self.pm = pymem.Pymem(process_name = FILE_NAME) # Change to a generic file name later ig
       
        self.addrStage = self.pm.base_address + ADDR_CURRENT_STAGE
        self.addrLives = self.pm.base_address + ADDR_LIVES
        self.addrBombs = self.pm.base_address + ADDR_BOMBS
        self.addrFunds = self.pm.base_address + ADDR_FUNDS
        self.addrCharacter = self.pm.base_address + ADDR_CURRENT_CHARACTER
        
        # Large pointers which hold lots of data.
        self.shopPtr = self.pm.base_address + ADDR_SHOP_PTR
        self.cardManagerPtr = self.pm.base_address + ADDR_CARD_MANAGER_PTR
        self.enemyManagerPtr = self.pm.base_address + ADDR_ENEMY_MANAGER_PTR
        
        self.mainMenuPtr = self.pm.base_address + ADDR_MAIN_MENU_PTR
        
        self.scorefilePtr = self.pm.base_address + ADDR_SCOREFILE_PTR
        
    '''
    Statics
    '''
    def getStage(self) -> int:
        return self.pm.read_int(self.addrStage)

    def getLives(self) -> int:
        return self.pm.read_int(self.addrLives)

    def setLives(self, value):
        self.pm.write_int(self.addrLives, value)

    def getFunds(self) -> int:
        return self.pm.read_int(self.addrFunds)

    def setFunds(self, value):
        self.pm.write_int(self.addrFunds, value)

    # Return values follow the character constants in stage_constants.py
    def getCurrentCharacter(self) -> int:
        return self.pm.read_int(self.addrCharacter)

    '''
    Main Menu Info
    '''


    '''
    Stage and Card Info
    '''

    # In a stage? If not, the player is in the main menu.
    # The pointer is only non-zero when in a stage.
    def inStage(self) -> bool:
        return self.pm.read_int(self.enemyManagerPtr) != 0

    # If there is an ID for a boss then there is a boss active.
    def isBossActive(self) -> bool:
        boss_address = getPointerAddress(self.pm, self.enemyManagerPtr, ADDR_BOSS_ID_OFFSET)
        return self.pm.read_int(boss_address) != 0

    # Returns current character.
    # 0 - Reimu
    # 1 - Marisa
    # 2 - Sakuya
    # 3 - Sanae
    def getCharacter(self):
        return self.pm.read_int(self.pm.base_address + ADDR_CURRENT_CHARACTER)

    # New speed is in the form [unfocused_speed, focused_speed]
    def setSpeed(self, new_speed):
        address = self.pm.read_int(self.pm.base_address + ADDR_PLAYER_PTR)
        address += 0x477B4
        speed = new_speed[0]
        self.pm.write_int(address + 0, speed)
        diagonal_speed = int(new_speed[0]/math.sqrt(2))
        self.pm.write_int(address + 4, diagonal_speed)

        speed = new_speed[1]
        self.pm.write_int(address + 8, speed)
        diagonal_speed = int(new_speed[1]/math.sqrt(2))
        self.pm.write_int(address + 12, diagonal_speed)

    def resetSpeed(self):
        speed_list = CHARACTER_SPEEDS[self.getCharacter()]

        address = self.pm.read_int(self.pm.base_address + ADDR_PLAYER_PTR)
        address += 0x477B4
        for i in range(4):
            self.pm.write_int(address + (i * 4), speed_list[i])

    def getCardCount(self):
        address = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_NUM_CARDS_OFFSET)
        return self.pm.read_int(address)

    # Cards are held in a linked list so we need to move throughout the list to find all references.
    def getCardAddresses(self, numCards) -> list:
        cards = []
        address_base = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_CARD_LIST_HEAD_OFFSET)

        for i in range(numCards):
            cards.append(address_base)
            
            address_base = address_base + 0x4
            address_base = self.pm.read_uint(address_base)

        return cards

    # Uses getCardAddresses to return the IDs of every card.
    def getCardIDs(self, numCards) -> list:
        card_id_list = []
        card_addresses = self.getCardAddresses(numCards)
        for card in card_addresses:
            id_address = getPointerAddress(self.pm, card, [0x4])

            card_id_list.append(self.pm.read_int(id_address))

        return card_id_list

    
    def disableCard(self, cardPtr):
        address = self.pm.read_int(cardPtr)
        self.pm.write_int(address, VTABLE_NULL_ADDR + self.pm.base_address)

    def enableCard(self, cardPtr):
        address = self.pm.read_int(cardPtr)
        card_id = self.pm.read_int(address + 0x4)
        vtable_address = CARD_ID_TO_VTABLE_ADDR[card_id] + self.pm.base_address
        self.pm.write_int(address, vtable_address)


    '''
    Shop Info
    '''
    def isShopActive(self) -> bool:
        return (self.pm.read_uint(self.shopPtr) != 0)

    def getShopCardCount(self) -> int:
        shopCount = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_ITEM_COUNT_OFFSET)
        return self.pm.read_int(shopCount)

    # Return all addresses found in the shop, they are stored in an array.
    def getShopCards(self, numCards) -> list:
        cards = []
        base_address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_CARD_LIST_OFFSET)
        for i in range(numCards):
            cards.append(self.pm.read_int(base_address))
            base_address += 0x4
        return cards

    # Position you are browsing over in the shop.
    def getShopCursorPosition(self) -> int:
        address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_CURSOR1_OFFSET)
        return self.pm.read_int(address)

    # 2 - Selecting a card
    # 5 - Yes/No to purchasing a card
    def getShopMenuState(self) -> int:
        address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_MENU_STATE_OFFSET)
        return self.pm.read_int(address)

    # Can be used to kick the player out of the shop purchasing option.
    def setShopMenuState(self, new_val):
        address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_MENU_STATE_OFFSET)
        self.pm.write_int(address, new_val)

    def setShopCard(self, pos, new_shop_card_id):
        base_address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_CARD_LIST_OFFSET)
        base_address += (pos * 0x4)
        self.pm.write_int(base_address, new_shop_card_id)

    '''
    Card Unlocks

    It should be noted that the order still works with card IDs despite them not being
    formatted in the same order in the unlocked cards menu.
    Thanks ZUN.
    '''
    def getCardUnlockedState(self, id) -> bool:
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_UNLOCKED_CARD_OFFSET)
        return self.pm.read_bytes(base_address + id, 1) == 1

    def setCardUnlockState(self, id, new_value):
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_UNLOCKED_CARD_OFFSET)
        self.pm.write_bytes(base_address + id, new_value, 1)