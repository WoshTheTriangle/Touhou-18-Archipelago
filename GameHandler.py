from .GameController import GameController
from .variables.card_constants import *
from .variables.stage_constants import *

class GameHandler:
    gameController = None
    bossesBeaten: dict = {}
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
            self.bossesBeaten[character] = [[False, False], [False, False], [False, False], [False, False], [False, False], [False, False]]
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

            



    def isCurrentBossDefeated(self, counter) -> bool:
        beenDefeated = false


        return beenDefeated

    def getStage(self) -> int:
        return self.gameController.getStage()

    def isShopActive(self) -> bool:
        return self.gameController.isShopActive()

    def getHeldCards(self) -> list:
        numCards = self.gameController.getCardCount()
        return self.gameController.getCards(numCards)

    def getShopCards(self) -> list:
        numCards = self.gameController.getShopCardCount()
        return self.gameController.getShopCards(numCards)