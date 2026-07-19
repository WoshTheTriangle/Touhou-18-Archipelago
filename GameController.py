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
from .variables.option_constants import *
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

        self.gameModePtr = self.pm.base_address + ADDR_GAME_MODE

        self.cardIconHead = self.pm.base_address + CARD_SMALL_ICON_HEAD
        

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

    def getGameMode(self) -> int:
        return self.pm.read_int(self.gameModePtr)

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

    def disableAllSpellCards(self) -> None:
        address = getPointerAddress(self.pm, self.scorefilePtr, [0x4CD60])
        for i in range(97):
            self.pm.write_int(address, 0)
            address += 0xDC

    def enableSpellCards(self, floor: int, ceiling: int) -> None:
        address = getPointerAddress(self.pm, self.scorefilePtr, [0x4CD60])
        address += (0xDC * floor)
        
        for i in range(ceiling - floor):
            self.pm.write_int(address, 1)
            address += 0xDC

    def check_if_in_game(self) -> bool:
        # Technically this only returns true if you are in the main menu,
        # but it would also be really inconvenient if the player connected anywhere
        # else so this will work just fine.
        if self.pm.read_int(self.mainMenuPtr) == 0:
            return False
        
        main_menu_select_area = self.getMainMenuSelectArea()

        if main_menu_select_area == 8 or (main_menu_select_area >= 18 and
        main_menu_select_area <= 20) or main_menu_select_area == 12:
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
        for i in range(4):
            self.pm.write_int(address, value)
            address += 4

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

    # Sets the menu restriction to the first 4 items of the array.
    def initMenuRestrict(self) -> None:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_SIZE_OFFSET)
        self.pm.write_int(address, 1)
        address += 4
        self.pm.write_int(address, 4)

    # Sets restrictions for options 0-3 in the list (characters or difficulties)
    def setMenuRestrict(self, restrict_list: list[bool]) -> None:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_HEAD_OFFSET)
        new_value = None

        # Write into the array of restricted values if the option is not available.
        for i in range(4):
            new_value = 5
            if not restrict_list[i]:
                new_value = i
            self.pm.write_int(address, new_value)
            address += 4

    # Sets restrictions for the characters in spellcard practice.
    def setSpellCardPracticeRestrict(self, restrict_list: list[bool]) -> None:
        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_SPELLCARD_PRACTICE_CHAR_SELECT)

        restrict_address = address + 68
        self.pm.write_int(restrict_address, 4)
        
        new_value = None
        for i in range(4):
            new_value = 5
            if not restrict_list[i]:
                new_value = i
            self.pm.write_int(address, new_value)
            address += 4

    # Sets restrictions for the difficulties in spellcard practice.
    def setSpellCardPracticeDifficultyRestrict(self, restrict_list: list[bool]) -> None:
        restrict_address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_SIZE_OFFSET)
        self.pm.write_int(restrict_address, 1)
        restrict_address += 4
        self.pm.write_int(restrict_address, 5)

        address = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_HEAD_OFFSET)
        for i in range(4):
            print(f"{i} {restrict_list[i]}")
            if not restrict_list[i]:
                self.pm.write_int(address, i)
            else:
                self.pm.write_int(address, 5)
            address += 4

        self.pm.write_int(address, 4)

    def setPracticeRestrict(self) -> None:
        extra_disabled = True

        address_size = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_SIZE_OFFSET)
        self.pm.write_int(address_size, 1)
        address_size += 4
        if self.pm.read_int(address_size) == 0:
            print("we have extra")
            extra_disabled = False
            self.pm.write_int(address_size, 2)
        else:
            self.pm.write_int(address_size, 3)

        address_practice = getPointerAddress(self.pm, self.mainMenuPtr, ADDR_MENU_RESTRICT_HEAD_OFFSET)
        self.pm.write_int(address_practice, 2)
        address_practice += 4
        #self.pm.write_int(address_practice, 3)
        #address_practice += 4
        self.pm.write_int(address_practice, 4)

        if extra_disabled:
            address_practice += 4
            self.pm.write_int(address_practice, 1)
        
    def clearInitialCards(self) -> None:
        address = getPointerAddress(self.pm, self.scorefilePtr, ADDR_INITIAL_CARDS_HELD_OFFSET)
        offset = 0
        while offset <= 64:
            self.pm.write_int(address, 0x38383838) 
            offset += 4

    def setInitialIconsBlank(self) -> None:
        for i in range(0, 50):
            if i >= 1 and i <= 6: continue # Item cards can stay.

            address = self.cardIconHead + (0x34 * i)
            self.pm.write_int(address, CARD_ID_TO_ICON_NUM[NULL_CARD])

    def setCardIcon(self, id: int) -> None:
        address = self.cardIconHead + (CARD_ID_TO_ICON_SPOT[id] * 0x34)
        self.pm.write_int(address, CARD_ID_TO_ICON_NUM[id])

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

    def setCardID(self, cardPtr: int, newVal: int) -> None:
        address = self.pm.read_int(cardPtr)
        self.pm.write_int(address + 4, newVal)

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

    def isCardAddressNull(self, cardPtr: int) -> bool:
        vtable_val = self.pm.read_int(cardPtr)
        vtable_val = self.pm.read_int(vtable_val)
        return vtable_val == (VTABLE_NULL_ADDR + self.pm.base_address)

    def getEquipmentOptionAddresses(self) -> list:
        return_list = []
        address = getPointerAddress(self.pm, self.playerPtr, EQUIPMENT_OPTION_OFFSET)
        while self.pm.read_int(address) == 2:
            return_list.append(address)
            address += EQUIPMENT_OPTION_SIZE

        return return_list

    # Updates the movement of an option object and controls whether it follows the player or not.
    def setEquipmentOption(self, address: int, y_offset: int, move_with_player: bool, equip_function: int) -> None:
        self.pm.write_int(address + EQUIPMENT_OPTION_Y_OFFSET - 4, 0) # X offset (I think this is only needed for Alice's card)

        self.pm.write_int(address + EQUIPMENT_OPTION_Y_OFFSET, y_offset)
        follow_player = 2 if move_with_player else 0
        self.pm.write_int(address + EQUIPMENT_OPTION_FOLLOW, follow_player)
        if not equip_function == 0:
            equip_function += self.pm.base_address
            self.pm.write_int(address + EQUIPMENT_OPTION_FUNCTION_OFFSET, equip_function)
        else:
            self.pm.write_int(address + EQUIPMENT_OPTION_FUNCTION_OFFSET, equip_function)

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