import pymem
import time
from .variables.address_shop import *
from .variables.card_constants import *
from .GameController import GameController
from .GameHandler import GameHandler

try:
    gameHandler = GameHandler()
    
    shop_viewed = False
    shop_address = 0
    
    shop_count = 0
    
    shop_count = 0
    
    while True:
        
        if gameHandler.isShopActive() and not shop_viewed:
            shop_viewed = True
            print("---SHOP INFO---")
            print(gameHandler.getShopCards())
        elif shop_address == 0:
            shop_viewed = False
            
        time.sleep(1)
        
        print(gameHandler.getHeldCards())
        
except Exception as e:
    print(f"got nothing, got {e}")