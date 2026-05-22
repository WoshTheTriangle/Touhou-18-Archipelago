import os
import pkgutil
import random
import traceback
import typing
from typing import Optional
import asyncio
import colorama
import orjson

from CommonClient import (
    CommonContext,
    ClientCommandProcessor,
    get_base_parser,
    logger,
    server_loop,
    gui_enabled
)

from NetUtils import NetworkItem
from .GameHandler import *
from .Locations import *
from .variables.meta_data import *
from .Items import *
from .variables import stage_constants
from .Tools import getStageLocationMapping, shop_card_id_to_card_id, getAPIDsForCards

class TouhouUMClientProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_test(self, reply = None) -> bool:
        """Commands to the command line"""
        changed = False

        if reply is not None:
            text = reply.lower()
            logger.info(f"{text}")
            changed = True

        return changed


class TouhouUMContext(CommonContext):
    """Touhou 18 Game Context"""
    handler = None

    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)

        self.items_handling = 0b111 # Items from your own world, other worlds, and starting start_inventory_from_pool
        # This needs to be self-defined otherwise the program cannot connect to the server.
        self.slot_data = True

        self.item_ap_id_to_name = None
        self.item_name_to_ap_id = None
        self.location_ap_id_to_name = None
        self.location_name_to_ap_id = None

        self.stage_location_mappings = []
        self.location_id_to_card_id = []

        self.able_to_check = False

        self.options = None
        self.in_error = None
        self.is_game_running: bool = False
        self.is_connected: bool = False
        self.loading_data_setup = True
        self.game: str = DISPLAY_NAME

        self.all_location_ids = []
        self.previous_location_checked = []
        self.command_processor = TouhouUMClientProcessor

        # Gameplay-related variables
        # This is the type of data that should be saved when closing the game.
        self.unlocked_characters: list = []
        self.unlocked_cards: list = []
        self.unlocked_stages: list = []

        # Deathlink variables
        self.deathlink_enabled: bool = False
        self.waiting_for_deathlink: bool = False
        self.caused_deathlink: bool = False
        self.died_to_deathlink: bool = False

        self.received_item_queue: list[NetworkItem] = [] # All items from the server.
        self.menu_item_queue: list = [] # Wait because player is in the menu.
        self.game_item_queue: list = [] # Wait because player is in a stage.

        self.all_received_items: list[int] = []
        self.loaded_past_received_items: bool = False
        self.last_received_item_index_server: int = -1

        self.reset()

    def reset(self) -> None:
        self.in_error = False
        self.loading_data_setup = True

        self.is_connected = False
        self.is_game_running = False

        self.all_location_ids = []
        self.previous_location_checked = []
        self.handler = None

        self.stage_location_mappings = []
        self.location_id_to_card_id = []

        self.unlocked_characters = []
        self.unlocked_cards = []
        self.unlocked_stages = []

        self.deathlink_enabled = False
        self.waiting_for_deathlink = False
        self.caused_deathlink = False
        self.died_to_deathlink = False

        self.received_item_queue = []
        self.menu_item_queue = []
        self.game_item_queue = []

        self.all_received_items = []
        self.loaded_past_received_items = False
        self.last_received_item_index_server = -1

    def reset_game_data(self):
        if self.handler == None: return
        if self.handler.gameController == None: return
        self.is_game_running = self.handler.GameController.check_if_in_game()

    def make_gui(self) -> None:
       ui = super().make_gui()
       ui.base_title = f"{DISPLAY_NAME} Client"
       return ui

    '''
    Connecting to the server and game process.
    '''

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def client_received_initial_server_data(self) -> bool:
        """
        If this method returns true then:
            - All LocationInfo packages have been received
            - DataPackage package received (id_to_name maps and name_to_id maps populated)
            - Connection package received (slot number populated)
            - RoomInfo package received (seed name populated)
        """
        return self.is_connected  

    async def wait_for_initial_connection_info(self):
        """
        Waits until the client has finished the initial conversation with the server.
        """
        if self.client_received_initial_server_data():
            return
        
        logger.info("Waiting for a connection from the server...")
        while not self.client_received_initial_server_data() and not self.exit_event.is_set():
            await asyncio.sleep(1)

    # Try to attach self to a game process.
    async def connect_to_game(self) -> None:
        """
        Attach client to game process
        """
        self.handler = None

        while self.handler == None:
            try:
                self.handler: GameHandler = GameHandler()
            except Exception as e:
                await asyncio.sleep(2)

    async def reconnect_to_game(self):
        """
        Reconnect to the game without resetting everything
        """
        while self.handler.gameController is None:
            try:
                self.handler.reconnect()
            except Exception as e:
                await asyncio.sleep(2)

    '''
    Handling sending packages and receiving packages.
    '''

    def on_package(self, cmd: str, args: dict):
        """
        Manage packages received from the server
        This is the big method.
        """
        if cmd == "RoomInfo":
            self.seed_name = args["seed_name"]

        if cmd == "Connected":
            self.previous_location_checked = args["checked_locations"]
            self.all_location_ids = set(args["missing_locations"] + args["checked_locations"])
            self.options = args["slot_data"] #Yaml options
            self.is_connected = True
            #TODO: Custom stuff and location mapping
            self.stage_location_mappings = getStageLocationMapping(self.options["split_by_difficulty"])
            self.location_id_to_card_id = getAPIDsForCards()

            if self.handler is not None:
                self.handler.reset()

            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": [DISPLAY_NAME]}]))

        if cmd == "ReceivedItems":
            # args["index"] is the next empty index of the list of items the player has.
            asyncio.create_task(self.handle_received_items(args["index"], args["items"]))
        elif cmd == "Retrieved":
            print("new")

        elif cmd == "DataPackage":
            if not self.all_location_ids:
                return
            self.location_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["location_name_to_id"]
            self.location_name_to_ap_id = {
                name: loc_id for name, loc_id in
                self.location_name_to_ap_id.items() if loc_id in self.all_location_ids
            }
            self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
            self.item_name_to_ap_id = args["data"]["games"][DISPLAY_NAME]["item_name_to_id"]
            self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}

        elif cmd == "Bounced":
            tags = args.get("tags", [])
        
        if cmd == "SetReply":
            print("g")

    def check_victory(self) -> bool:
        print("soon")

    async def handle_received_items(self, network_index, network_items_list):
        # When network_index = 0, it contains all items given to the client.
        print(network_items_list)
        print(network_index)
        id_list = [network_item.item for network_item in network_items_list]
        print(id_list)

        local_list_length = len(self.all_received_items)
        new_items_list: list[NetworkItem] = []

        # You'd want to be in the game if you are to receive stuff.
        while self.handler is None or self.handler.gameController is None:
            await asyncio.sleep(0.5)

        # All items are here
        if network_index <= 0:

            # Some desync has occurred between the server and client.
            if len(network_index) < local_list_length:
                logger.info("Error: Client has more items than the server's received item list")
                self.all_received_items = []
                for item in id_list:
                    self.all_received_items.append(item)

                #TODO th18.5 saved everything to a json. idk if I should do that as well.
                # I'll find out if I do when I trap myself in a corner.
                return

            new_items_list = network_items_list[local_list_length:]

        else:
            if local_list_length == network_index:
                new_items_list = network_items_list
            # A desync has occurred
            else:
                sync_msg = [{"cmd": "Sync"}]
                # TODO locations checked?
                await self.send_msgs(sync_msg)

        if len(new_items_list) <= 0: return

        self.all_received_items.append(id_list)

        handle_items(new_items_list)

    async def update_locations_checked(self):
        new_locations = []

        # Stage-related Locations
        for id, map in self.stage_location_mappings.items():
            if self.handler.isBossBeaten(*map) and id not in self.previous_location_checked:
                new_locations.append(id)

        for id, card_id in self.location_id_to_card_id.items():
            if id not in self.previous_location_checked and self.handler.hasCardBeenPurchased(card_id):
                new_locations.append(id)
        

        # If there are any new locations, add them to the list and send them to the server.
        if new_locations:
            print("the new")
            self.previous_location_checked += new_locations
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

    async def send_deathlink(self):
        """
        Send deathlink to the server if server is active.
        """
        # Don't send anything if deathlink is not enabled.
        if not self.deathlink_enabled: return

        await self.send_death(self.player_names[self.slot] + "Has died")


    '''
    Handling Item List
    '''
    
    def handle_items(self, item_list):
        if len(item_list) <= 0: return

        for ap_item in item_list:
            item_id = ap_item.item

    #TODO
    # Items that can only be processed while the player is in-stage.        
    async def handle_game_only_items(self):
        for item_id in self.game_item_queue:
            print("tba")

            self.menu_item_queue.remove(item_id)

    #TODO
    # These items can be processed anywhere at any time.
    def handle_menu_items(self):
        for item_id in self.menu_item_queue:
            print("tba")

            self.menu_item_queue.remove(item_id)
    

    '''
    Async Loops
    '''

    async def game_loop(self):
        """
        The main loop that handles giving stage resources and updating boss-related locations.
        Stuff that happens while in-stage
        """
        try:
            boss_present = False
            current_lives = 0
            boss_counter = -1
            given_resources = False
            current_score = 0
            current_power = 0
            current_continue = 0
            current_stage = 0
            

            currently_in_stage = True
            currently_in_shop = False

            game_state = -1

            shop_card_list = []
            shop_card_id_list = []
            player_card_list = []
            
            new_card_list = []

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(0.5)

                game_state = self.handler.get_game_state()

                if game_state == -1:
                        continue

                # Despite there being no menus between stages, this will still
                # reset itself every stage because the shop is its own state.
                # self.able_to_check is going to be moderated by the menu and shop loops
                if game_state == IN_STAGE and self.able_to_check:

                    # The games have begun.
                    # Started a new game or entered a new stage.
                    if not currently_in_stage:
                        currently_in_stage = True
                        boss_counter = -1
                        boss_present = False
                        current_score = self.handler.getScore()
                        current_continue = self.handler.getContinues()
                        current_stage = self.handler.getStage()

                        temp_value = 0

                        if False: #TODO add state to see impossible stuff
                            self.able_to_check = False

                    if not given_resources:
                        await asyncio.sleep(0.5)
                        #TODO give player resources

                        # Disable stuff we don't have unlocked
                        self.handler.updateCardLockState()
                        given_resources = True
                        current_lives = self.handler.getLives()

                    if current_score <= self.handler.getScore() or current_continue > self.handler.getContinues():
                        # Player's score could have lowered due to using a continue.
                        current_score = self.handler.getScore()
                        current_continue = self.handler.getContinues()
                    else:
                        # Player has restarted the game.
                        logger.info("Restarted the game")
                        currently_in_stage = False
                        given_resources = False
                        continue
                    # Check score for that.

                    # Check for if a boss appeared.
                    if not boss_present:
                        if self.handler.isBossActive():
                            boss_present = True
                            boss_counter += 1
                    else:
                        if boss_present:
                            # Boss slain.
                            if not self.handler.isBossActive():
                                if not self.handler.isCurrentBossDefeated(boss_counter):
                                    self.handler.setCurrentBossDefeated(boss_counter)
                                    await self.update_locations_checked()
                                boss_present = False

                    # Did the player die?
                    new_lives = self.handler.getLives()
                    if current_lives != new_lives:
                        # Seems they gained a Life
                        if current_lives > new_lives:
                            self.handler.setBombs(3) # made up a number for now TODO fix later
                        current_lives = new_lives

                # Went to main menu or shop.
                elif currently_in_stage:
                    currently_in_stage = False
                    given_resources = False

                '''Shop Check'''
                if game_state == IN_SHOP:
                    # Entering Shop
                    if not currently_in_shop:
                        
                        current_power = self.handler.getPower()
                        currently_in_shop = True
                        logger.info("Entered a shop")
                        player_card_list = self.handler.getHeldCards()

                        # Disabling cards that have been purchased before but are not unlocked.
                        shop_card_list = self.handler.getShopCards()
                        shop_card_id_list = shop_card_id_to_card_id(self.handler, shop_card_list)
                        for i in range(len(shop_card_list)):   
                            if (self.handler.cardsPurchased[shop_card_id_list[i]] 
                            and not self.handler.cardsUnlocked[shop_card_id_list[i]]):
                                self.handler.disableCard(shop_card_list[i])

                # Leaving Shop    
                elif currently_in_shop:
                    logger.info("Left a shop")
                    currently_in_shop = False
                    new_card_list = self.handler.getHeldCards()
                    print(f"Player cards {player_card_list}")
                    print(f"New cards {new_card_list}")

                    # New possible starting card was purchased.
                    if new_card_list[-1] != player_card_list[-1]:
                        if not self.handler.hasCardBeenPurchased(new_card_list[-1]):
                            self.handler.purchaseCard(new_card_list[-1])
                            
                            # If the card has not been received via Archipelago, set it to still be locked
                            # so it cannot be equipped from the main menu.
                            if not self.handler.hasCardBeenReceived(new_card_list[-1]):
                                self.handler.setCardUnlockState(new_card_list[-1], False)    

                    # Purchased an item card such as a Life Card or Nazrin's Card (Unequippable at start)
                    # Idea is to check if it is not in the purchased list in the handler but it is unlocked in-game.
                    # This can only be true if you just bought the card so engage in purchasing and undo the effects
                    # from the card if it has not been received as an item yet.
                    # Previous section is much less complex since you can easily view the cards the player is holding.
                    else:
                        print("a")
                        if (not self.handler.hasCardBeenPurchased(LIFE_CARD) 
                        and self.handler.getCardUnlockedState(LIFE_CARD)): 
                            print("a")
                            self.handler.purchaseCard(LIFE_CARD)
                            if not self.handler.hasCardBeenReceived(LIFE_CARD):
                                temp_value = self.handler.getLives()
                                self.handler.setLives(temp_value - 1)
                        if (not self.handler.hasCardBeenPurchased(BOMB_CARD) 
                        and self.handler.getCardUnlockedState(BOMB_CARD)): 
                            print("a")
                            self.handler.purchaseCard(BOMB_CARD)
                            if not self.handler.hasCardBeenReceived(BOMB_CARD):
                                temp_value = self.handler.getBombs()
                                self.handler.setBombs(temp_value - 1)
                        if (not self.handler.hasCardBeenPurchased(NAZRIN_CARD) 
                        and self.handler.getCardUnlockedState(NAZRIN_CARD)): 
                            print("a")
                            self.handler.purchaseCard(NAZRIN_CARD)
                            if not self.handler.hasCardBeenReceived(NAZRIN_CARD):
                                self.handler.addFunds(-50)
                        if (not self.handler.hasCardBeenPurchased(RINGO_CARD) 
                        and self.handler.getCardUnlockedState(RINGO_CARD)):
                            print("a")
                            self.handler.purchaseCard(RINGO_CARD)
                            if not self.handler.hasCardBeenReceived(RINGO_CARD):
                                player.setPower(current_power)
                        if (not self.handler.hasCardBeenPurchased(MOKOU_CARD) 
                        and self.handler.getCardUnlockedState(MOKOU_CARD)):
                            print("a")
                            self.handler.purchaseCard(MOKOU_CARD)
                            if not self.handler.hasCardBeenReceived(MOKOU_CARD):
                                temp_value = self.handler.getLives()
                                self.handler.setLives(temp_value - 3)
                    
                    await self.update_locations_checked()

        except Exception as e:
            logger.error(f"Main ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def menu_loop(self):
        """
		Loop for dealing with main menu stuff
		"""
        print("new")

        try:
            game_state = -1
            currently_in_menu = False

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(0.5)

                game_state = self.handler.get_game_state()
                if game_state == IN_MENU:
                    # Entered the menu or just connected to the game.
                    if not currently_in_menu:
                        logger.info("Entered main menu")
                        self.able_to_check = True
                        currently_in_menu = True

                elif currently_in_menu:
                    logger.info("Left main menu")
                    currently_in_menu = False

        except Exception as e:
            logger.error(f"Main ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    '''
    async def shop_loop(self):
        """
        Loop which handles shop stuff such as editing cards 
        and checking whether a new card was purchased or not
        """
        try:
            game_state = -1
            

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(0.5)
                game_state = self.handler.get_game_state()
                if game_state == IN_SHOP:
                    if not currently_in_shop:
                        currently_in_shop = True
                        logger.info("Entered a shop")
                    
                elif currently_in_shop:
                    logger.info("Left a shop")
                    currently_in_shop = False

        except Exception as e:
            logger.error(f"Main ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True
    '''

    async def trap_loop(self):
        """
        Loop that handles traps.
        """
        print("soon")

    async def death_link_loop(self):
        """
        Loop that hanldes death link.
        """
        print("soon")

    async def message_loop(self):
        """
        Loop which handles displaying messages.
        """
        print("soon")

async def game_watcher(ctx):
    """
    The main client loop which watches the gameplay process.
    If connection is lost, it will reconnect.
    """
    # ctx is the Context Client Instance

    await ctx.wait_for_initial_connection_info()
    # await ctx.initial_load_last_item_list()

    while not ctx.exit_event.is_set():
        # Client disconnected from the server.
        if not ctx.server:
            logger.info("Disconnected from server, trying to reconnect...")
            ctx.reset()
            await ctx.wait_for_initial_connection_info()

        if ctx.handler == None and not ctx.in_error:
            logger.info(f"Connecting to {SHORT_NAME}...")
            asyncio.create_task(ctx.connect_to_game())
            while(ctx.handler == None and not ctx.exit_event.is_set()):
                await asyncio.sleep(1)

        if ctx.in_error:
            logger.info(f"An error has broken connection. Waiting for connection to {SHORT_NAME}")
            ctx.handler.gameController = None
            asyncio.create_task(ctx.reconnect_to_game())
            await asyncio.sleep(1)
            while(ctx.handler.gameController == None and not ctx.exit_event.is_set()):
                await asyncio.sleep(1)

        if ctx.handler and ctx.handler.gameController:
            ctx.in_error = False

            if not ctx.is_game_running:
                ctx.is_game_running = ctx.handler.gameController.check_if_in_game()
                await asyncio.sleep(1)
                continue

        if ctx.loading_data_setup:
            logger.info(f"{SHORT_NAME} process found. Beginning game loop.")
            ctx.loading_data_setup = False
            continue
            

        logger.info("Beginning main loops")
        client_loops = []
        client_loops.append(asyncio.create_task(ctx.game_loop()))
        client_loops.append(asyncio.create_task(ctx.menu_loop()))
        #client_loops.append(asyncio.create_task(ctx.shop_loop()))
        # Add more loops later

        await ctx.update_locations_checked()
        #TODO: Update Stage List

        #TODO: Death Link stuff

        #TODO: Edit handler as needed

        # If all is going well, we can just loop forever.
        while not ctx.exit_event.is_set() and ctx.server and not ctx.in_error:
            await asyncio.sleep(1)

        # We left the infinite loop so either the player left, server broke, or an error occurred.
        # End all loops.
        for loop in client_loops:
            try:
                loop.cancel()
            except:
                pass

def launch():
    """
    Launch a client instance
    """

    async def main(args):
        """
        Threaded client instance
        """
        ctx = TouhouUMContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx))
        if gui_enabled: ctx.run_gui()
        ctx.run_cli()
        watcher = asyncio.create_task(
            game_watcher(ctx),
            name="GameProgressionWatcher"
        )
        await ctx.exit_event.wait()
        await watcher
        await ctx.shutdown()

    parser = get_base_parser(description=SHORT_NAME + " Client")
    args, _ = parser.parse_known_args()

    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()