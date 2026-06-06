import pymem
import pymem.exception
import math

from .variables.address_main_menu import *
from .variables.address_shop import *
from .variables.address_stage import *
from .variables.address_cards import *
from .variables.stage_constants import *
from .variables.card_constants import *
from .variables.meta_data import *
from .Tools import *


class GameController:
    '''Memory accessing class'''

    def __init__(self):
        self.pm = pymem.Pymem(process_name = FILE_NAME) # Change to a generic file name later ig
        self.addrStage = self.pm.base_address + ADDR_CURRENT_STAGE
        self.addrLives = self.pm.base_address + ADDR_LIVES
        self.addrBombs = self.pm.base_address + ADDR_BOMBS
        self.addrLifeFrag = self.pm.base_address + ADDR_LIFE_FRAGS
        self.addrBombFrag = self.pm.base_address + ADDR_BOMB_FRAGS
        self.addrFunds = self.pm.base_address + ADDR_FUNDS
        self.addrCharacter = self.pm.base_address + ADDR_CURRENT_CHARACTER
        self.addrPower = self.pm.base_address + ADDR_POWER
        self.addrScore = self.pm.base_address + ADDR_SCORE
        self.addrContinues = self.pm.base_address + ADDR_CONTINUES
        self.addrDifficulty = self.pm.base_address + ADDR_DIFFICULTY
        
        self.addrTimeInStage = self.pm.base_address + ADDR_TIME_IN_STAGE

        # Large pointers which hold lots of data.
        self.shopPtr = self.pm.base_address + ADDR_SHOP_PTR
        self.cardManagerPtr = self.pm.base_address + ADDR_CARD_MANAGER_PTR
        self.enemyManagerPtr = self.pm.base_address + ADDR_ENEMY_MANAGER_PTR
        
        self.playerPtr = self.pm.base_address + ADDR_PLAYER_PTR
        self.mainMenuPtr = self.pm.base_address + ADDR_MAIN_MENU_PTR
        self.scorefilePtr = self.pm.base_address + ADDR_SCOREFILE_PTR
        self.menuStatePtr = self.pm.base_address + ADDR_MENU_STATE
        self.guiPtr = self.pm.base_address + ADDR_GUI_PTR
        

    '''
    Statics
    '''
    def getStage(self) -> int:
        return self.pm.read_int(self.addrStage)

    def getScore(self) -> int:
        return self.pm.read_int(self.addrScore)

    def setScore(self, value: int) -> None:
        return self.pm.write_int(self.addrScore, value)

    def getLives(self) -> int:
        return self.pm.read_int(self.addrLives)

    def setLives(self, value: int) -> None:
        self.pm.write_int(self.addrLives, value)

    def getBombs(self) -> int:
        return self.pm.read_int(self.addrBombs)

    def setBombs(self, value: int) -> None:
        self.pm.write_int(self.addrBombs, value)

    def getLifeFrags(self) -> int:
        return self.pm.read_int(self.addrLifeFrag)

    def setLifeFrags(self, value: int) -> None:
        self.pm.write_int(self.addrLifeFrag, value)

    def getBombFrags(self) -> int:
        return self.pm.read_int(self.addrBombFrag)

    def setBombFrags(self, value: int) -> None:
        self.pm.write_int(self.addrBombFrag, value)

    def getFunds(self) -> int:
        return self.pm.read_int(self.addrFunds)

    def setFunds(self, value: int) -> None:
        self.pm.write_int(self.addrFunds, value)

    def getDifficulty(self) -> int:
        return self.pm.read_int(self.addrDifficulty)

    def setDifficulty(self, value: int) -> None:
        self.pm.write_int(self.addrDifficulty, value)

    def getPower(self) -> int:
        return self.pm.read_int(self.addrPower)

    def setPower(self, value: int) -> None:
        self.pm.write_int(self.addrPower, value)

    def getTimeInStage(self) -> int:
        return self.pm.read_int(self.addrTimeInStage)

    # States:
    # 0 - Not present
    # 1 - Normal
    # 2 - Spawning in (coming up from the bottom)
    # 3 - Invincible and unable to move
    # 4 - Dead
    def getPlayerState(self) -> int:
        address = getPointerAddress(self.pm, self.playerPtr, ADDR_PLAYER_STATE_OFFSET)
        return self.pm.read_int(address)

    # The only real state of importance is 4 since that kills the player.
    def setPlayerState(self, value: int) -> None:
        address = getPointerAddress(self.pm, self.playerPtr, ADDR_PLAYER_STATE_OFFSET)
        self.pm.write_int(address, value)

    # Return values follow the character constants in stage_constants.py
    # 0 - Reimu
    # 1 - Marisa
    # 2 - Sakuya
    # 3 - Sanae
    def getCurrentCharacter(self) -> int:
        return self.pm.read_int(self.addrCharacter)

    def getContinues(self) -> int:
        return self.pm.read_int(self.addrContinues)

    def setContinues(self, value: int) -> None:
        self.pm.write_int(self.addrContinues, value)

    # Sets the gui element for lives or bombs to on or off.
    def setGuiState(self, gui_id: int, life: bool, new_state: bool) -> None:
        new_val = GUI_ACTIVE if new_state else GUI_UNACTIVE
        gui_id *= 4
        life_bomb_base = ADDR_LIFE_GUI_ELEMENT_OFFSET_HEAD if life else ADDR_BOMB_GUI_ELEMENT_OFFSET_HEAD
        address = getPointerAddress(self.pm, self.guiPtr, [life_bomb_base + gui_id, ADDR_GUI_STATE_OFFSET])
        
        #print(f"{gui_id/4} = {hex(address)}")
        self.pm.write_int(address, new_val)

    def guiExists(self) -> bool:
        gui_address = self.pm.read_int(self.guiPtr)
        if gui_address == 0:
            return False
        
        gui_values = self.pm.read_int(gui_address + ADDR_LIFE_GUI_ELEMENT_OFFSET_HEAD)
        return gui_values != 0

    '''
    Main Menu Info
    '''

    def in_main_menu(self) -> bool:
        if self.pm.read_int(self.mainMenuPtr) == 0:
            return False
        return True

    def getMainMenuSelect(self) -> int:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_SELECT)
        return self.pm.read_int(address)

    def setMainMenuSelect(self, value: int) -> None:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_SELECT)
        self.pm.write_int(address, value)

    def getMainMenuSelectArea(self) -> int:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_LOCATION_OFFSET)
        return self.pm.read_int(address)

    def check_if_in_game(self) -> bool: #TODO, make it actually anywhere
        # Technically this only returns true if you are in the main menu,
        # but it would also be really inconvenient if the player connected anywhere
        # else so this will work just fine.
        if self.pm.read_int(self.mainMenuPtr) == 0:
            return False
        return True

    # Will force the player back into the main menu when in-stage.
    def force_to_main_menu(self) -> None:
        #print("Force B")
        self.pm.write_int(self.menuStatePtr, 4)

    def getCardSlotCount(self) -> int:
        address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_CARD_SLOTS_OFFSET)
        return self.pm.read_int(address)

    def setCardSlotCount(self, value: int) -> None:
        address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_CARD_SLOTS_OFFSET)
        self.pm.write_int(address, value)

    # Unlocks or locks extra stage for a character chosen.
    def setExtraStageUnlock(self, character: int, lock_status: bool) -> None:
        lock_status = 1 if lock_status else 0
        address = self.pm.read_int(self.scorefilePtr)
        address += ADDR_SCOREFILE_CHARACTER_OFFSET

        character_offset = character * ADDR_SCOREFILE_SHOTTYPE_SIZE

        address += character_offset + ADDR_DIFFICULTIES_BEATEN_OFFSET

        for i in range(5):
            self.pm.write_int(address + (i * 4), lock_status)

    # This is only going to be used to see if we are entering the extra stage.
    def getOptionCount(self) -> int:
        return self.pm.read_int(self.mainMenuPtr + ADDR_SELECTION_OPTION_COUNT)

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

    # New speed is in the form [unfocused_speed, focused_speed].
    def setSpeed(self, new_speeds: list[int]) -> None:
        address = self.pm.read_int(self.pm.base_address + ADDR_PLAYER_PTR)
        address += 0x477B4
        speed = new_speeds[0]
        self.pm.write_int(address + 0, speed)
        diagonal_speed = int(new_speeds[0]/math.sqrt(2))
        self.pm.write_int(address + 4, diagonal_speed)

        speed = new_speeds[1]
        self.pm.write_int(address + 8, speed)
        diagonal_speed = int(new_speeds[1]/math.sqrt(2))
        self.pm.write_int(address + 12, diagonal_speed)

    # Resets character to default speed.
    def resetSpeed(self) -> None:
        speed_list = CHARACTER_SPEEDS[self.getCurrentCharacter()]

        address = self.pm.read_int(self.pm.base_address + ADDR_PLAYER_PTR)
        address += 0x477B4
        for i in range(4):
            self.pm.write_int(address + (i * 4), speed_list[i])

    # Returns the amount of cards the player is holding.
    def getCardCount(self) -> None:
        address = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_NUM_CARDS_OFFSET)
        return self.pm.read_int(address)

    # Cards are held in a linked list so we need to move throughout the list to find all references.
    # Each node has 0x0 - *Current_Entry, 0x4 - *Next_Entry, 0x8 - *Previous_Entry
    def getCardAddresses(self, numCards: int) -> list:
        cards = []
        address_base = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_CARD_LIST_HEAD_OFFSET)

        for i in range(numCards):
            cards.append(address_base)
            
            address_base = address_base + 0x4
            address_base = self.pm.read_uint(address_base)

        return cards

    # Uses getCardAddresses to return the IDs of every card.
    def getCardIDs(self, numCards: int) -> list:
        card_id_list = []
        card_addresses = self.getCardAddresses(numCards)
        for card in card_addresses:
            id_address = getPointerAddress(self.pm, card, [0x4])

            card_id_list.append(self.pm.read_int(id_address))

        return card_id_list

    # Puts the null vtable in the vtable for a card, essentially disabling it.
    def disableCard(self, cardPtr: int) -> None:
        address = self.pm.read_int(cardPtr)
        self.pm.write_int(address, VTABLE_NULL_ADDR + self.pm.base_address)

    # Inserts the card's regular vtable back into it, making it act as normal.
    def enableCard(self, cardPtr: int) -> None:
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
    def getShopCards(self, numCards: int) -> list:
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
    def setShopMenuState(self, new_val: int) -> None:
        address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_MENU_STATE_OFFSET)
        self.pm.write_int(address, new_val)

    # Doesn't override the graphic but it does override what is being purchased.
    def setShopCard(self, pos: int, new_shop_card_id: int) -> None:
        base_address = getPointerAddress(self.pm, self.shopPtr, ADDR_SHOP_CARD_LIST_OFFSET)
        base_address += (pos * 0x4)
        self.pm.write_int(base_address, new_shop_card_id)

    '''
    Card Unlocks and Achievements

    It should be noted that the order still works with card IDs despite them not being
    formatted in the same order in the unlocked cards menu.
    Thanks ZUN.
    '''
    def getCardUnlockedState(self, id: int) -> bool:
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_UNLOCKED_CARD_OFFSET)
        return self.pm.read_bytes(base_address + id, 1) == bytes([1])

    def setCardUnlockState(self, id: int, new_value: int) -> None:
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_UNLOCKED_CARD_OFFSET)
        self.pm.write_bytes(base_address + id, bytes([new_value]), 1)

    def getAchievementState(self, id: int) -> bool:
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_ACHIEVEMENT_OFFSET)
        return self.pm.read_bytes(base_address + id, 1) == bytes([1])

    def setAchievementState(self, id: int, new_value: int) -> None:
        base_address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_ACHIEVEMENT_OFFSET)
        self.pm.write_bytes(base_address + id, bytes([new_value]), 1)