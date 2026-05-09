import pymem
import pymem.exception

from .Tools import *
from .variables.address_main_menu import *
from .variables.address_shop import *
from .variables.address_stage import *



class GameController:
    '''Memory accessing class'''

    def __init__(self):
        
        self.pm = pymem.Pymem(process_name = "th18.exe") # Change to a generic file name later ig
       
        self.addrStage = self.pm.base_address + ADDR_CURRENT_STAGE
        self.addrLives = self.pm.base_address + ADDR_LIVES
        self.addrBombs = self.pm.base_address + ADDR_BOMBS
        self.addrFunds = self.pm.base_address + ADDR_FUNDS
        
        # Large pointers which hold lots of data.
        self.shopPtr = self.pm.base_address + ADDR_SHOP_PTR
        self.cardManagerPtr = self.pm.base_address + ADDR_CARD_MANAGER_PTR
        self.enemyManagerPtr = self.pm.base_address + ADDR_ENEMY_MANAGER_PTR
        
        self.mainMenuPtr = self.pm.base_address + ADDR_MAIN_MENU_PTR
        
        self.scorefilePtr = self.pm.base_address + ADDR_SCOREFILE_PTR
        
        

    

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

    def addFunds(self, value):
        newFunds = self.getFunds() + value
        self.pm.write_int(self.addrFunds, newFunds)

    def isShopActive(self) -> bool:
        return (self.pm.read_uint(self.shopPtr) != 0)

    def getNumCards(self):
        address = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_NUM_CARDS_OFFSET)
        return self.pm.read_int(address)

    # Cards are held in a linked list so we need to move throughout the list to find all IDs
    def getCards(self, numCards) -> list:
        cards = []
        address_base = getPointerAddress(self.pm, self.cardManagerPtr, ADDR_CARD_LIST_HEAD_OFFSET)

        for i in range(numCards):
            id_address = getPointerAddress(self.pm, address_base, [0x4])

            cards.append(self.pm.read_int(id_address))
            
            address_base = address_base + 0x4
            address_base = self.pm.read_uint(address_base)

        return cards

