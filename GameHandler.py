from .GameController import GameController
from .variables.card_constants import *
from .variables.stage_constants import *

class GameHandler:
    gameController = None
    bossesBeaten: dict = {}
    extraBeaten: dict = {}
    stagesUnlocked: dict = {}
    cardsUnlocked: list = []
    cardsPurchased: list = []
    charactersUnlocked: dict = {}

    difficultiesUnlocked = []

    extraUnlocked: dict = {}
    previousLocationChecked = []

    def __init__(self):
        ''' 
        This class is a wrapper for GameController
        while also storing any saved data about the game
        '''

        self.gameController = GameController()
        self.reset()
        self.init_game()


    def reconnect(self):
        self.gameController = GameController()
        self.init_game(self)
        
        
    def init_game(self):
        print("init game todo")
        #TODO

    def reset(self) -> None:
        for character in CHARACTERS:
            self.bossesBeaten[character] = {}
            for difficulty in range(4):
                self.bossesBeaten[character][difficulty] = [[False, False], [False, False], [False, False], 
                                                            [False, False], [False, False], [False, False],
                                                            [False, False]]

            self.extraBeaten[character] = [[False, False]]

            self.extraUnlocked[character] = False

        self.charactersUnlocked[CHARACTER_MARISA] = False
        self.charactersUnlocked[CHARACTER_SAKUYA] = False
        self.charactersUnlocked[CHARACTER_SANAE] = False

        self.difficultiesUnlocked = [False, False, False, True, False]

        # No cards unlocked so far.
        self.cardsPurchased = [False] * 56
        self.cardsUnlocked = [False] * 56

        for i in range(1, 7):
            self.stagesUnlocked[i] = False

            
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
        elif stage == 7: # Extra Stage
            bossBeaten = self.extraBeaten[character][counter]
        elif difficulty == -1: # Regular game without difficulties checked
            for all_difficulties in range(4):
                bossBeaten = self.bossesBeaten[character][all_difficulties][stage][counter] or bossBeaten

        return bossBeaten

    # Set the boss you just defeated for the first time to defeated by checking it off in the list.
    def setCurrentBossDefeated(self, counter, check_difficulties: bool = False, check_lower_difficulties: bool = False) -> None:
        currentStage = self.getStage()
        current_difficulty = self.getDifficulty()
        
        if (currentStage == 7):
            self.extraBeaten[self.gameController.getCurrentCharacter()][counter] = True
        else:
            self.bossesBeaten[self.gameController.getCurrentCharacter()][self.getDifficulty()][self.gameController.getStage() - 1][counter] = True
            
            if check_lower_difficulties:
                if difficultiesUnlocked[DIFFICULTY_EASY]:
                    self.bossesBeaten[self.gameController.getCurrentCharacter()][EASY][self.gameController.getStage() - 1][counter] = True
                if difficultiesUnlocked[DIFFICULTY_NORMAL] and current_difficulty >= 1:
                    self.bossesBeaten[self.gameController.getCurrentCharacter()][NORMAL][self.gameController.getStage() - 1][counter] = True
                if difficultiesUnlocked[DIFFICULTY_HARD] and current_difficulty >= 2:
                    self.bossesBeaten[self.gameController.getCurrentCharacter()][HARD][self.gameController.getStage() - 1][counter] = True
        

    '''
    General Getters and Setters
    '''

    def inStage(self) -> bool:
        return self.gameController.inStage()

    def getStage(self) -> int:
        return self.gameController.getStage()

    def getCurrentCharacter() -> int:
        return self.gameController.getCurrentCharacter()

    def getScore(self) -> int:
        return self.gameController.getScore()

    def getFunds(self) -> int:
        return self.gameController.getFunds()

    def setFunds(self, value) -> None:
        self.gameController.setFunds(value)

    def addFunds(self, value) -> None:
        newFunds = self.gameController.getFunds() + value
        self.gameController.setFunds(newFunds)

    def getContinues(self) -> int:
        return self.gameController.getContinues()

    def setContinues(self, value) -> None:
        self.gameController.setContinues(value)

    def getLives(self) -> int:
        self.gameController.getLives()

    def setLives(self, value) -> None:
        self.gameController.setLives(value)

    def getBombs(self) -> int:
        self.gameController.getBombs()

    def setBombs(self, value) -> None:
        self.gameController.setBombs(value)

    def getDifficulty(self) -> int:
        return self.gameController.getDifficulty()

    def setSpeed(self, new_speed) -> None:
        self.gameController.setSpeed(new_speed)

    def resetSpeed(self) -> None:
        self.gameController.resetSpeed()

    def isShopActive(self) -> bool:
        return self.gameController.isShopActive()

    def getHeldCards(self) -> list:
        numCards = self.gameController.getCardCount()
        return self.gameController.getCardIDs(numCards)

    def getCardAddresses(self) -> list:
        cardCount = self.gameController.getCardCount()
        return self.gameController.getCardAddresses(cardCount)    


    # If a card isn't unlocked but is purchased, disable it.
    # The re-enabling is in case the card gets checked while they own a disabled one.
    def updateCardLockState(self) -> None:
        card_addresses = self.getCardAddresses()
        card_ids = self.getHeldCards()
        for i in range(len(card_addresses)):
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
        original_shop_card_id += self.gameController.pm.base_address
        card_list = self.getShopCards()

        # Card is not present.
        if(card_list.count(original_shop_card_id) <= 0):
            return
        
        pos = card_list.index(original_shop_card_id)
        
        if(pos > 0 and pos < self.gameController.getShopCardCount()):
            self.gameController.setShopCard(pos, new_shop_card_id)