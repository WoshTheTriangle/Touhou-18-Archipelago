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

        # No cards unlocked so far.
        self.cardsPurchased = [False] * 56
        self.cardsUnlocked = [False] * 56

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

    def setSpeed(self, new_speed):
        self.gameController.setSpeed(new_speed)

    def resetSpeed(self):
        self.gameController.resetSpeed()

    def isShopActive(self) -> bool:
        return self.gameController.isShopActive()

    def getHeldCards(self) -> list:
        numCards = self.gameController.getCardCount()
        return self.gameController.getCardIDs(numCards)

    def getCardAddresses(self) -> list:
        cardCount = self.gameController.getCardCount()
        return self.gameController.getCardAddresses(cardCount)    

    '''
        def disableNotUnlockedCards(self):
            card_addresses = self.getCardAddresses()
            card_ids = self.getHeldCards()
            for i in range(len(card_addresses)):
                if(self.cardsUnlocked[card_ids[i]] == False):
                    self.gameController.disableCard(card_addresses[i])
                    print("DENIED")

        def enableUnlockedCards(self):
            card_addresses = self.getCardAddresses()
            card_ids = self.getHeldCards()
            for i in range(len(card_addresses)):
                if(self.cardsUnlocked[card_ids[i]] == True):
                    self.gameController.enableCard(card_addresses[i])
                    print("you're in")
    '''
    # If a card isn't unlocked but is purchased, disable it.
    # The re-enabling is in case the card gets checked while they own a disabled one.
    def updateCardLockState(self):
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
    def setShopCard(self, original_shop_card_id, new_shop_card_id):
        new_shop_card_id += self.gameController.pm.base_address
        original_shop_card_id += self.gameController.pm.base_address
        card_list = self.getShopCards()

        if(card_list.count(original_shop_card_id) <= 0):
            return
        
        pos = card_list.index(original_shop_card_id)
        
        if(pos > 0 and pos < self.gameController.getShopCardCount()):
            self.gameController.setShopCard(pos, new_shop_card_id)