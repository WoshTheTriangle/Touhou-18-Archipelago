from .GameController import GameController
from .variables.card_constants import *
from .variables.stage_constants import *
from .variables.address_shop import *
from .Tools import clamp

class GameHandler:
    gameController = None

    initial_lives = 0
    initial_bombs = 0

    max_lives = 0
    max_bombs = 0

    continues = 0
    cardSlots = 1

    latestStageIndex = 0

    bossesBeaten: dict = {}
    extraBeaten: dict = {}
    stagesUnlocked: dict = {}
    cardsUnlocked: list = []
    cardsPurchased: list = []
    charactersUnlocked: dict = {}

    unlocked_card_count = 0

    endingCompleted: dict = {}
    altEndingCompleted: dict = {}
    extraCompleted: dict = {}

    difficultiesUnlocked = []

    previousLocationChecked = []

    def __init__(self, card_locations_checked: list[int] = None):
        ''' 
        This class is a wrapper for GameController
        while also storing any saved data about the game
        '''

        self.gameController = GameController()
        self.reset()
        self.init_game(card_locations_checked)

    def reconnect(self):
        self.gameController = GameController()
        self.init_game(self)
        
    # Change settings within the game to initialize it for Archipelago
    def init_game(self, card_locations_checked: list[int] = None):
        for i in range(56):
            self.setCardUnlockState(i, 0)

        for i in range(30):
            self.setAchievementState(i, False)
        
        self.setCardSlotCount(1)

        for character in CHARACTERS:
            self.set_extra_stage_unlock(character, False)

        for card_id in card_locations_checked:
            self.cardsPurchased[card_id] = True

        self.clearInitialCards()

        self.setInitialIconsBlank()

        self.disableAllSpellCards()

        # Enable stage 1 spellcard practice
        self.enableSpellCards(0, 8)


    def reset(self) -> None:

        # Default values
        initial_lives = 0
        initial_bombs = 0

        max_lives = 0
        max_bombs = 0

        continues = 0
        cardSlots = 1
        latestStageIndex = 1

        unlocked_card_count = 0

        for character in CHARACTERS:
            self.bossesBeaten[character] = {}
            for difficulty in range(4):
                self.bossesBeaten[character][difficulty] = [[False, False], [False, False], [False, False], 
                                                            [False, False], [False, False], [False, False],
                                                            [False, False]]

            self.extraBeaten[character] = [False, False]

            self.endingCompleted[character] = False
            self.altEndingCompleted[character] = False
            self.extraCompleted[character] = False

        self.charactersUnlocked[CHARACTER_REIMU] = False
        self.charactersUnlocked[CHARACTER_MARISA] = False
        self.charactersUnlocked[CHARACTER_SAKUYA] = False
        self.charactersUnlocked[CHARACTER_SANAE] = False

        self.difficultiesUnlocked = [False, False, False, True, True]

        # No cards ed so far.
        self.cardsPurchased = [False] * 56
        self.cardsUnlocked = [False] * 56

        # Stage 1 is unlocked
        for character in CHARACTERS:
            self.stagesUnlocked[character] = {}
            self.stagesUnlocked[character][1] = True

            for i in range(2, 8):
                self.stagesUnlocked[character][i] = False

            
    def unlock_character(self, character: int) -> None:
        value = self.charactersUnlocked.get(character, -1)
        
        if value == -1:
            print("Tried to unlock a character which does not exist")
            return
        
        self.charactersUnlocked[character] = True

    def unlock_extra(self, character: int = -1) -> None:
        spellcard_floor = 97 - SPELLCARD_COUNT_PER_STAGE[7]
        spellcard_ceiling = 97
        self.enableSpellCards(spellcard_floor, spellcard_ceiling)

        if character == -1:
            for each_character in CHARACTERS:
                self.stagesUnlocked[each_character][7] = True
            return
            
        self.stagesUnlocked[character][7] = True

    def get_game_state(self) -> int:
        if self.gameController.isShopActive():
            return IN_SHOP
        elif self.gameController.inStage():
            return IN_STAGE
        elif self.gameController.in_main_menu():
            return IN_MENU

        # If we get here, something is seriously wrong.
        return -1        

    def isBossActive(self) -> bool:
        return self.gameController.isBossActive()

    # Check if the boss you just beat has already been beaten before.
    def isCurrentBossDefeated(self, counter) -> bool:
        beenDefeated = False
        currentStage = self.gameController.getStage()
        difficulty = self.getDifficulty()

        if(currentStage < 7):
            beenDefeated = self.bossesBeaten[self.gameController.getCurrentCharacter()][difficulty][self.gameController.getStage()][counter]
        elif (currentStage == 7):
            beenDefeated = self.extraBeaten[self.gameController.getCurrentCharacter()][counter]

        return beenDefeated

    # General check if a midboss/boss from a certain stage has been beaten by a certain character at a certain difficulty.
    # Difficulty is set to -1 if difficulty is not a check.
    def isBossBeaten(self, character, stage, counter, difficulty = -1) -> bool:
        bossBeaten = False
        if difficulty >= 0 and difficulty < 4: # Regular game with difficulties checked
            bossBeaten = self.bossesBeaten[character][difficulty][stage][counter]
        elif stage == 6: # Extra Stage
            bossBeaten = self.extraBeaten[character][counter]
        elif difficulty == -1: # Regular game without difficulties checked
            for all_difficulties in range(4):
                bossBeaten = self.bossesBeaten[character][all_difficulties][stage][counter] or bossBeaten

        return bossBeaten

    # Check if goal conditions from the goal map has been completed.
    def isGoalCompleted(self, character, goal_id) -> bool:
        goal_completed = False

        if goal_id == GOAL_CHIMATA:
            for difficulty in range(4):
                goal_completed = goal_completed or self.bossesBeaten[character][difficulty][5][1]
                #goal_completed = self.bossesBeaten[character][1]
        elif goal_id == GOAL_MOMOYO:
            goal_completed = self.extraBeaten[character][1]
        elif goal_id == GOAL_CHIMATA_BLANK:
            goal_completed = self.getAchievementState(character * 2)

        if goal_completed:
            print("chimata successfully checked")
        return goal_completed

    # Essentially hashing completions for review in checking if goals have been met.
    def setGoalCompleted(self, character: int, goal_id: int) -> None:
        if goal_id == GOAL_CHIMATA:
            self.endingCompleted[character] = True
        elif goal_id == GOAL_MOMOYO:
            self.extraCompleted[character] = True
        elif goal_id == GOAL_CHIMATA_BLANK:
           self.altEndingCompleted[character] = True

    # Set the boss you just defeated for the first time to defeated by checking it off in the list.
    def setCurrentBossDefeated(self, counter, check_difficulties: bool = False, check_lower_difficulties: bool = False) -> None:
        currentStage = self.getStage()
        current_difficulty = self.getDifficulty()
        current_character = self.gameController.getCurrentCharacter()
        
        if (currentStage == 7):
            print("extra stage beat thing")
            self.extraBeaten[current_character][counter] = True
        else:
            self.bossesBeaten[current_character][self.getDifficulty()][self.gameController.getStage() - 1][counter] = True
            
            if check_lower_difficulties:
                if difficultiesUnlocked[DIFFICULTY_EASY]:
                    self.bossesBeaten[current_character][EASY][self.gameController.getStage() - 1][counter] = True
                if difficultiesUnlocked[DIFFICULTY_NORMAL] and current_difficulty >= DIFFICULTY_NORMAL:
                    self.bossesBeaten[current_character][NORMAL][self.gameController.getStage() - 1][counter] = True
                if difficultiesUnlocked[DIFFICULTY_HARD] and current_difficulty >= DIFFICULTY_HARD:
                    self.bossesBeaten[current_character][HARD][self.gameController.getStage() - 1][counter] = True
    
    '''
    Main Menu Stuff
    '''
    def getMainMenuSelectArea(self) -> int:
        return self.gameController.getMainMenuSelectArea()

    # Select state in main menu (e.g., character currently being chosen).
    def getMainMenuSelect(self) -> int:
        return self.gameController.getMainMenuSelect()

    def setMainMenuSelect(self, value: int) -> None:
        value = clamp(0, 3, value)
        return self.gameController.setMainMenuSelect(value)

    def disableAllSpellCards(self) -> None:
        self.gameController.disableAllSpellCards()

    def enableSpellCards(self, floor: int, ceiling: int) -> None:
        self.gameController.enableSpellCards(floor, ceiling)

    # Force the player back to the main menu from anywhere.
    def forceToMainMenu(self) -> None:
        print("Force A")
        self.gameController.force_to_main_menu()

    # Unlocks or locks extra stage for a character chosen.
    def set_extra_stage_unlock(self, character: int, lock_status: bool) -> None:
        self.gameController.setExtraStageUnlock(character, lock_status)

    def getOptionCount(self) -> int:
        return self.gameController.getOptionCount()

    def setDifficultyRestrict(self) -> None:
        self.gameController.initMenuRestrict()
        self.gameController.setMenuRestrict(self.difficultiesUnlocked)

    def setCharacterRestrict(self) -> None:
        self.gameController.initMenuRestrict()
        self.gameController.setMenuRestrict(self.charactersUnlocked)

    def setPracticeRestrict(self) -> None:
        self.gameController.setPracticeRestrict()
        if self.getMainMenuSelect() >= 2 and self.getMainMenuSelect() <= 4:
            self.setMainMenuSelect(0)

    def setSpellCardPracticeRestrict(self) -> None:
        restrict_list = [self.charactersUnlocked[CHARACTER_REIMU],self.charactersUnlocked[CHARACTER_MARISA],
                        self.charactersUnlocked[CHARACTER_SAKUYA], self.charactersUnlocked[CHARACTER_SANAE]]
        self.gameController.setSpellCardPracticeRestrict(restrict_list)

    def setSpellCardPracticeDifficultyRestrict(self) -> None:
        self.gameController.setSpellCardPracticeDifficultyRestrict(self.difficultiesUnlocked)

    def clearInitialCards(self) -> None:
        self.gameController.clearInitialCards()

    def setInitialIconsBlank(self) -> None:
        self.gameController.setInitialIconsBlank()

    '''
    General Getters and Setters
    '''

    def inStage(self) -> bool:
        return self.gameController.inStage()

    def getStage(self) -> int:
        return self.gameController.getStage()

    def getTimeInStage(self) -> int:
        return self.gameController.getTimeInStage()

    def getCurrentCharacter(self) -> int:
        return self.gameController.getCurrentCharacter()

    def getScore(self) -> int:
        return self.gameController.getScore()

    def setScore(self, value: int) -> None:
        self.gameController.setScore(value)

    def getFunds(self) -> int:
        return self.gameController.getFunds()

    def setFunds(self, value) -> None:
        self.gameController.setFunds(value)

    def getContinues(self) -> int:
        return self.gameController.getContinues()

    def setContinues(self, value) -> None:
        self.gameController.setContinues(clamp(0, 5, value))

    def getLives(self) -> int:
        return self.gameController.getLives()

    def setLives(self, value) -> None:
        self.gameController.setLives(clamp(0, 7, value))

        self.updateLivesGUI()

    def getBombs(self) -> int:
        return self.gameController.getBombs()

    def setBombs(self, value: int) -> None:
        self.gameController.setBombs(clamp(0, 7, value))

        self.updateBombsGUI()

    def getLifeFrags(self) -> int:
        return self.gameController.getLifeFrags()

    def setLifeFrags(self, value) -> None:
        self.gameController.setLifeFrags(value)

    def getBombFrags(self) -> int:
        return self.gameController.getBombFrags()

    def setBombFrags(self, value) -> None:
        self.gameController.setBombFrags(value)

    def setMaxLives(self, value: int) -> None:
        value = clamp(0, 7, value)
        self.max_lives = value

    def setMaxBombs(self, value: int) -> None:
        value = clamp(0, 7, value)
        self.max_bombs = value

    def getPower(self) -> int:
        return self.gameController.getPower()

    def setPower(self, value):
        self.gameController.setPower(value)

    def getDifficulty(self) -> int:
        return self.gameController.getDifficulty()

    # This is a guardrail in the main menu.
    # Using this outside of the main menu is a really bad idea.
    def setDifficulty(self, value) -> None:
        value = clamp(0, 3, value)
        self.gameController.setDifficulty(value)

    def setSpeed(self, new_speeds: list[int]) -> None:
        self.gameController.setSpeed(new_speeds)

    def isShopActive(self) -> bool:
        return self.gameController.isShopActive()

    def getHeldCards(self) -> list:
        numCards = self.gameController.getCardCount()
        return self.gameController.getCardIDs(numCards)

    def getCardAddresses(self) -> list:
        cardCount = self.gameController.getCardCount()
        return self.gameController.getCardAddresses(cardCount)    

    def getCardUnlockedState(self, id: int) -> bool:
        if id == 56: return True
        return self.gameController.getCardUnlockedState(id)

    def setCardUnlockState(self, id: int, new_state: bool) -> None:
        if id == 56: return

        new_val = 0
        if new_state: new_val = 1
        self.gameController.setCardUnlockState(id, new_val)

    def setGameCardUnlockStates(self) -> None:
        '''
        This is to make it so all cards that have not been purchased have the "New!" icon above them.
        '''
        for i in range(56):
            self.gameController.setCardUnlockState(i, self.cardsPurchased[i])

    def setDefaultCardUnlockStates(self) -> None:
        '''
        Return the card unlock states back to normal in menus.
        '''
        for i in range(56):
            self.gameController.setCardUnlockState(i, self.cardsUnlocked[i])

    def getAchievementState(self, id: int) -> bool:
        return self.gameController.getAchievementState(id)

    def setAchievementState(self, id: int, new_state: bool) -> None:
        new_val = 0
        if new_state: new_val = 1
        self.gameController.setAchievementState(id, new_val)

    def setCardSlotCount(self, value: int) -> None:
        value = clamp(0, 32, value)
        self.gameController.setCardSlotCount(value)

    def getPlayerState(self) -> int:
        return self.gameController.getPlayerState()

    '''
    Helper Functions
    '''
    
    def addFunds(self, value) -> None:
        newFunds = clamp(0, 100000, self.gameController.getFunds() + value)
        self.gameController.setFunds(newFunds)

    # The game does not automatically add lives and bombs when you set the amount of fragments
    # to a number 3 or above so we need to do it manually.
    def addLifeFrags(self, amount) -> None:
        life_frags = self.getLifeFrags() + amount
        extra_lives = int(life_frags/3)
        
        self.setLives(self.getLives() + extra_lives)
        self.setLifeFrags(life_frags % 3)

    def addBombFrags(self, amount) -> None:
        bomb_frags = self.getBombFrags() + amount
        extra_bombs = int(bomb_frags/3)
        
        self.setBombs(self.getBombs() + extra_bombs)
        self.setBombFrags(bomb_frags % 3)

    # Since you cannot add options via editing power numbers, we will simply leave it at the closest X.99 or 4.00
    def addPower(self, value) -> None: 
        current_power = self.gameController.getPower()
        hundred_cap = ((current_power // 100) * 100) + 100

        # Edge case if power is 4.00
        if hundred_cap == 500: hundred_cap = 401

        newPower = clamp(0, hundred_cap - 1, current_power + value)
        self.gameController.setPower(newPower)
    
    def addInitialLives(self) -> None:
        self.initial_lives = clamp(0, 7, self.initial_lives + 1)

    def addInitialBombs(self) -> None:
        self.initial_bombs = clamp(0, 7, self.initial_bombs + 1)

    def addMaxLives(self) -> None:
        self.max_lives = clamp(0, 7, self.max_lives + 1)

    def addMaxBombs(self) -> None:
        self.max_bombs = clamp(0, 7, self.max_bombs + 1)

    def addContinues(self) -> None:
        self.continues = clamp(0, 5, self.continues + 1)

    def addCardSlots(self) -> None:
        self.cardSlots = clamp(0, 3, self.cardSlots + 1)

    def addStage(self, character: int = -1) -> None:
        index = 1
        spellcard_floor = 0
        spellcard_ceiling = 0

        if character == -1:
            while index < 8:
                if not self.stagesUnlocked[CHARACTER_REIMU][index]: # Reimu is a default character to check.

                    for i in range(index):     
                        spellcard_floor += SPELLCARD_COUNT_PER_STAGE[i]

                    spellcard_ceiling = spellcard_floor + SPELLCARD_COUNT_PER_STAGE[index]
                    self.enableSpellCards(spellcard_floor, spellcard_ceiling)

                    for each_character in CHARACTERS:
                        self.stagesUnlocked[each_character][index] = True
                    return
                index += 1

            return
        
        while index < 8:
            if not self.stagesUnlocked[character][index]:
                for i in range(index):
                    spellcard_floor += SPELLCARD_COUNT_PER_STAGE[i]
                spellcard_ceiling = spellcard_floor + SPELLCARD_COUNT_PER_STAGE[index]
                
                self.enableSpellCards(spellcard_floor, spellcard_ceiling)

                self.stagesUnlocked[character][index] = True
                return
            index += 1

    def lowerDifficulty(self) -> None:

        index = 2
        while index >= 0:
            if not self.difficultiesUnlocked[index]:
                self.difficultiesUnlocked[index] = True
                return
            index -= 1

    def excludeLunatic(self) -> None:
        self.difficultiesUnlocked[3] = False

    def resetSpeed(self) -> None:
        self.gameController.resetSpeed()

    def killPlayer(self) -> None:
        self.gameController.setPlayerState(4)

    def updateLivesGUI(self) -> None:
        lives = self.gameController.getLives()
        for i in range(7):
            if i < lives:
                self.gameController.setGuiState(i, True, True)
            else:
                self.gameController.setGuiState(i, True, False)

    def updateBombsGUI(self) -> None:
        bombs = self.gameController.getBombs()
        for i in range(7):
            if i < bombs:
                self.gameController.setGuiState(i, False, True)
            else:
                self.gameController.setGuiState(i, False, False)

    def guiExists(self) -> bool:
        return self.gameController.guiExists()

    '''
    Managing GameHandler variables
    '''

    def shop_card_id_to_card_id(self, shop_card_list: list):
        base_address = self.gameController.pm.base_address
        return_list = []
        for shop_card in shop_card_list:
            return_list.append(SHOP_CARD_ID_TO_CARD_ID[shop_card - base_address])

        return return_list


    def hasCardBeenPurchased(self, id: int) -> bool:
        # Account for null card
        if id == 56: return True

        return self.cardsPurchased[id]

    def purchaseCard(self, id) -> None:
        self.cardsPurchased[id] = True

    def hasCardBeenReceived(self, id: int) -> bool:
        if id == 56: return True

        return self.cardsUnlocked[id]

    def receiveCard(self, id: int) -> None:
        if id == 56: return

        self.cardsUnlocked[id] = True

    def setCardIcon(self, id: int) -> None:
        self.gameController.setCardIcon(id)

    def isStageUnlocked(self, character: int, stage_num: int) -> bool:
        print(f"{character} {stage_num}")
        print(self.stagesUnlocked[character][stage_num])
        return self.stagesUnlocked[character][stage_num]

    def isDifficultyUnlocked(self, difficulty: int) -> bool:
        return self.difficultiesUnlocked[difficulty]

    def isCharacterUnlocked(self, character: int) -> bool:
        return self.charactersUnlocked[character]

    def getHandlerCardSlotCount(self) -> int:
        return self.cardSlots

    def get_extra_unlock_status(self, character: int) -> bool:
        return self.stagesUnlocked[character][7]

    def add_to_unlocked_card_count(self) -> None:
        self.unlocked_card_count += 1

    def get_unlocked_card_count(self) -> int:
        return self.unlocked_card_count

    def get_game_mode(self) -> int:
        return self.gameController.getGameMode()

    def setCardID(self, cardPtr: int, newVal: int) -> None:
        self.gameController.setCardID(cardPtr, newVal)

    '''
    Shop Settings
    '''

    # If a card isn't unlocked but is purchased, disable it.
    # The re-enabling is in case the card gets checked while they own a disabled one.
    def updateCardLockState(self) -> None:
        card_addresses = self.getCardAddresses()
        card_ids = self.getHeldCards()
        for i in range(len(card_addresses)):
            # Null Card
            if card_ids[i] == 56: continue
            
            if(self.cardsUnlocked[card_ids[i]] == False):
                self.gameController.disableCard(card_addresses[i])
                print("DENIED")
            elif(self.cardsUnlocked[card_ids[i]] == True):
                self.gameController.enableCard(card_addresses[i])
                print("We are in")


    def getShopCards(self) -> list:
        numCards = self.gameController.getShopCardCount()
        return self.gameController.getShopCards(numCards)

    def doesShopContainCard(self, shop_card_id) -> bool:
        card_list = self.getShopCards()
        return card_list.count(self.gameController.pm.base_address + shop_card_id) > 0

    # Use the shop addresses found in address_shop.py for both shop card IDs
    def setShopCard(self, original_shop_card_id, new_shop_card_id) -> None:
        new_shop_card_id += self.gameController.pm.base_address
        #original_shop_card_id += self.gameController.pm.base_address
        card_list = self.getShopCards()

        # Card is not present.
        if(card_list.count(original_shop_card_id) <= 0):
            return
        
        pos = card_list.index(original_shop_card_id)
        
        if(pos >= 0 and pos < self.gameController.getShopCardCount()):
            self.gameController.setShopCard(pos, new_shop_card_id)

    def disableCard(self, shop_card_id) -> None:
        self.setShopCard(shop_card_id, NULL_SHOP_ADDR)
