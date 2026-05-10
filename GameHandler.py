from .GameController import GameController
from .variables.card_constants import *
from .variables.stage_constants import *

class GameHandler:
    gameController = None
    bossesBeaten: dict = {}
    extraBeaten: dict = {}
    stagesUnlocked: dict = {}
    cardsUnlocked: dict = {}
    cardsPurchased: dict = {}
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



    def reset(self):
        for character in CHARACTERS:
            self.bossesBeaten[character] = [[False, False], [False, False], [False, False], 
                                            [False, False], [False, False], [False, False],
                                            [False, False]]

            self.extraBeaten[character] = [[False, False]]

            self.extraUnlocked[character] = False

        self.charactersUnlocked[CHARACTER_MARISA] = False
        self.charactersUnlocked[CHARACTER_SAKUYA] = False
        self.charactersUnlocked[CHARACTER_SANAE] = False

        self.difficultiesUnlocked = [False, False, False, True, False]

        for i in range(56):
            self.cardsPurchased[i] = False
            self.cardsUnlocked[i] = False

        for i in range(1, 7):
            self.stagesUnlocked[i] = False

            

    def isBossActive(self) -> bool:
        return self.gameController.isBossActive()

    def isCurrentBossDefeated(self, counter) -> bool:
        beenDefeated = False
        currentStage = self.gameController.getStage()
        
        if(currentStage < 7):
            beenDefeated = self.bossesBeaten[self.gameController.getCurrentCharacter()][self.gameController.getStage()][counter]
        elif (currentStage == 7):
            beenDefeated = self.extraBeaten[self.gameController.getCurrentCharacter()][counter]

        return beenDefeated

    def setCurrentBossDefeated(self, counter):
        currentStage = self.gameController.getStage()
        
        if(currentStage < 7):
            self.bossesBeaten[self.gameController.getCurrentCharacter()][self.gameController.getStage()][counter] = True
        elif (currentStage == 7):
            self.extraBeaten[self.gameController.getCurrentCharacter()][counter] = True

    def inStage(self) -> bool:
        return self.gameController.inStage()

    def getStage(self) -> int:
        return self.gameController.getStage()

    def getFunds(self) -> int:
        return self.gameController.getFunds()

    def setFunds(self, value):
        self.gameController.setFunds(value)

    def addFunds(self, value):
        newFunds = self.gameController.getFunds() + value
        self.gameController.setFunds(newFunds)

    def isShopActive(self) -> bool:
        return self.gameController.isShopActive()

    def getHeldCards(self) -> list:
        numCards = self.gameController.getCardCount()
        return self.gameController.getCards(numCards)

    def getShopCards(self) -> list:
        numCards = self.gameController.getShopCardCount()
        return self.gameController.getShopCards(numCards)