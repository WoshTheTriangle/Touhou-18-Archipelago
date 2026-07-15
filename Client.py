import os
import pkgutil
import random
import time
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
from .variables import stage_constants, card_constants
from .Tools import *

def get_death_link_message(deathlink_trigger: int = DEATHLINK_TRIGGER_LIFE) -> str:
    if DEATHLINK_TRIGGER_GAMEOVER: return random.choice(DEATH_LINK_GAMEOVER_MSGS + DEATH_LINK_GENERIC_MSGS)
    else: return random.choice(DEATH_LINK_LIFE_MSGS + DEATH_LINK_GENERIC_MSGS)

class TouhouUMClientProcessor(ClientCommandProcessor):
    def __init__(self, ctx):
        super().__init__(ctx)

    def _cmd_deathlink(self, new_state: str = None) -> None:
        """
        Toggle Death Link on or off.
        If no arguments are given, will respond with current Death Link status.
        :param active: If "on" or "true", enable Death Link. If "off" or "false", disable Death Link.
        """
        changed = False

        if not self.ctx.is_connected:
            logger.info("Not connected to the server.")
            return

        if new_state != None:
            if new_state.lower() in ["on", "true"]:  
                logger.info("Death Link Enabled")
                if "DeathLink" not in self.ctx.tags:
                    self.ctx.tags.add("DeathLink")
                    self.ctx.deathlink_enabled = True
                    changed = True
            elif new_state.lower() in ["off", "false"]:
                if "DeathLink" in self.ctx.tags:
                    self.ctx.tags.remove("DeathLink")
                    self.ctx.deathlink_enabled = False
                    changed = True
                logger.info("Death Link Disabled")
            else:
                logger.info("Invalid argument, use 'on' or 'off'")

            if changed:
                asyncio.create_task(self.ctx.send_msgs([{"cmd": "ConnectUpdate", "tags": self.ctx.tags}]))
            return

        logger.info(f"Death Link status: {self.ctx.deathlink_enabled}")
        if not self.ctx.deathlink_enabled: return

        if self.ctx.deathlink_trigger == DEATHLINK_TRIGGER_LIFE:
            logger.info("Death Link on Life Loss")
        elif self.ctx.deathlink_trigger == DEATHLINK_TRIGGER_GAMEOVER:
            logger.info("Death Link on Game Over")

    def _cmd_deathlink_trigger(self, trigger: str = None) -> None:
        """
        Get or set when a Death Link is triggered. Leave blank to check status.
        :param trigger: Upon Life Loss ("life"), Upon Game Over ("game_over").
        """
        if not self.ctx.is_connected:
            logger.info("Not connected to the server.")
            return

        if not self.ctx.deathlink_enabled:
            logger.info("Deathlink is not enabled.")
            return

        if trigger is None:
            if self.ctx.deathlink_trigger == DEATHLINK_TRIGGER_LIFE:
                logger.info("Death Link on Life Loss")
            elif self.ctx.deathlink_trigger == DEATHLINK_TRIGGER_GAMEOVER:
                logger.info("Death Link on Game Over")
            else:
                logger.info("Death Link Condition is Unknown")
        else:
            if trigger.lower() in ["life"]:
                self.ctx.deathlink_trigger = DEATHLINK_TRIGGER_LIFE
                logger.info("Death Link Condition has been set to: 'Life Loss'")
            elif trigger.lower() in ["game_over"]:
                self.ctx.deathlink_trigger = DEATHLINK_TRIGGER_GAMEOVER
                logger.info("Death Link Condition has been set to: 'Game Over'")
            else:
                logger.info("Invalid Death Link trigger argument")

    def _cmd_deathlink_amnesty(self, value: int = -1) -> None:
        """
        Get or Set the number of death before sending a Death Link.
        If no arguments are given, will respond with the current amnesty count.
        :param value: Set the amnesty to this value, must be between 0 and 10.
        """
        if not self.ctx.is_connected:
            logger.info("Not connected to the server.")
            return

        if self.ctx.handler is not None and self.ctx.handler.gameController is not None:
            if value == -1:
                logger.info(f"Current Death Link Amnesty is set to: {self.ctx.deathlink_amnesty}")
                return
            else:
                value = int(value)
                if value < 0 or value > 10:
                    logger.info("Invalid argument, amnesty value must be between 0 and 10")
                    return
                
                self.ctx.deathlink_amnesty = value
                logger.info(f"New Death Link Amnesty Value is: {self.ctx.deathlink_amnesty}")

    def _cmd_ringlink(self, new_state: str = None) -> None:
        """
        Toggle Ring Link on or off.
        If no arguments are given, will respond with the current state of Ring Link.
        :param active: If "on" or "true", enable Ring Link. If "off" or "false", disable Ring Link.
        """
        changed = False

        if not self.ctx.is_connected:
            logger.info("Not connected to the server.")
            return

        if new_state != None:
            if new_state.lower() in ["on", "true"]:  
                logger.info("Ring Link Enabled")
                if "RingLink" not in self.ctx.tags:
                    self.ctx.tags.add("RingLink")
                    self.ctx.ring_link_enabled = True
                    changed = True
            elif new_state.lower() in ["off", "false"]:
                if "RingLink" in self.ctx.tags:
                    self.ctx.tags.remove("RingLink")
                    self.ctx.ring_link_enabled = False
                    changed = True
                logger.info("Ring Link Disabled")
            else:
                logger.info("Invalid argument, use 'on' or 'off'")

            if changed:
                asyncio.create_task(self.ctx.send_msgs([{"cmd": "ConnectUpdate", "tags": self.ctx.tags}]))
            return

        logger.info(f"Ring Link status: {self.ctx.ring_link_enabled}")

    def _cmd_cards(self, state: str = None) -> None:
        """
        Check what cards you have or have not purchased in your Touhou 18 world.
        If no argument is given, will default to listing cards that have not been purchased.
        :param trigger: If "Purchased" or "True" will list cards that have been purchased.
                        If "Not_Purchased" or "False" will list cards that have not been purchased.
        """
        
        if not self.ctx.is_connected:
            logger.info("Not connected to the server.")
            return

        count = 0
        if state == None or state.lower() in ["not_purchased", "false"]:
            logger.info("Cards Not Purchased:")
            for id in self.ctx.missing_locations:
                if "Purchased" in location_id_to_name[id]:
                    card_name = (location_id_to_name[id].split("Purchased "))[1]
                    logger.info(card_name)
                    count += 1
            logger.info(f"Number of cards not purchased: {count}/52")
        elif state.lower() in ["purchased", "true"]:
            logger.info("Cards Purchased:")
            for id in self.ctx.previous_location_checked:
                if "Purchased" in location_id_to_name[id]:
                    card_name = (location_id_to_name[id].split("Purchased "))[1]
                    logger.info(card_name)
                    count += 1
            logger.info(f"Number of cards purchased: {count}/52")
        else:
            logger.info("Incorrect argument given. Use 'Purchased' or 'Not_Purchased'")
        

            
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
        self.location_id_to_ending_mapping = []

        self.able_to_check = False

        self.retrieved_last_item_id = False

        self.options = None
        self.in_error = None
        self.is_game_running: bool = False
        self.is_connected: bool = False
        self.loading_data_setup = True
        self.game: str = DISPLAY_NAME

        self.location_semaphore_in_use = False

        self.magatama_id: int = 0
        self.blank_card_id: int = 0

        self.all_location_ids: list = []
        self.previous_location_checked: list = []

        self.command_processor = TouhouUMClientProcessor

        # Gameplay-related variables
        self.checked_if_owns_stage = False

        self.unlocked_characters: list = []
        self.unlocked_cards: list = []
        self.unlocked_stages: list = []

        # Deathlink variables
        self.deathlink_enabled: bool = False
        self.deathlink_trigger: int = None
        self.deathlink_amnesty: int = None

        self.waiting_for_deathlink: bool = False
        self.caused_deathlink: bool = False
        self.died_to_deathlink: bool = False
        self.last_death_link: float = None

        # Ringlink variables
        self.ring_link_enabled: bool = False
        self.last_funds: int = 0
        self.last_ring_link: float = 0
        self.ring_link_id: int = None

        self.received_item_queue: list[NetworkItem] = [] # All items from the server.
        self.card_item_queue: list = [] # Contains card-related items.
        self.permanent_item_queue: list = [] # General permanent items such as continues and stages.
        self.game_item_queue: list = [] # Can only be active while in-stage.

        self.all_received_items: list[int] = []
        self.loaded_past_received_items: bool = False

        self.last_received_item_index_server: int = -1

        self.custom_data_keys_list: list = None
        self.data_sent = False

        self.reset()

    def reset(self) -> None:
        self.in_error = False
        self.loading_data_setup = True

        self.is_connected = False
        self.is_game_running = False

        self.retrieved_last_item_id = False

        self.all_location_ids = []
        self.previous_location_checked = []
        self.handler = None

        self.stage_location_mappings = []
        self.location_id_to_card_id = []
        self.location_id_to_ending_mapping = []

        self.checked_if_owns_stage = False

        self.location_semaphore_in_use = False

        self.magatama_id = 0
        self.blank_card_id = 0

        self.unlocked_characters = []
        self.unlocked_cards = []
        self.unlocked_stages = []

        self.deathlink_enabled = False
        self.deathlink_trigger = DEATHLINK_TRIGGER_LIFE
        self.deathlink_amnesty = 1

        self.waiting_for_deathlink = False
        self.caused_deathlink = False
        self.died_to_deathlink = False
        self.last_death_link = 0

        self.ring_link_enabled = False
        self.last_funds = 0
        self.last_ring_link = 0
        self.ring_link_id = None

        self.received_item_queue = []
        self.card_item_queue = []
        self.permanent_item_queue = []
        self.game_item_queue = []

        self.all_received_items = []
        self.loaded_past_received_items = False

        self.last_received_item_index_server = -1
        self.data_sent = False

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

        # Let the handler know we have already checked these card locations beforehand.
        card_location_list = []
        for id in self.previous_location_checked:
            if "Purchased" in location_id_to_name[id]:
                card_name = (location_id_to_name[id].split("Purchased "))[1]
                card_location_list.append(NAME_TO_CARD_ID[card_name])
            
            

        while self.handler == None:
            try:
                self.handler: GameHandler = GameHandler(card_location_list)
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
        This is the big networking method for the receiving part of it.
        """

        if cmd == "RoomInfo":
            self.seed_name = args["seed_name"]

        if cmd == "Connected": # Initial connection data
            self.previous_location_checked = args["checked_locations"]
            self.all_location_ids = set(args["missing_locations"] + args["checked_locations"])
            self.options = args["slot_data"] #Yaml options
            self.is_connected = True


            self.slot = args["slot"]
            self.custom_data_keys_list = [f"{str(self.team)}_{str(self.slot)}_LastItemIndexTH18"] 

            self.stage_location_mappings = getStageLocationMapping(self.options["difficulty_check"])
            self.location_id_to_card_id = getAPIDsForCards()
            self.location_id_to_ending_mapping = getLocationIDsToEndingMapping()

            self.blank_card_id = location_table[f"Unlocked {BLANK_CARD_NAME}"]
            self.magatama_id = location_table[f"Unlocked {MAGATAMA_CARD_NAME}"]

            if self.handler is not None:
                self.handler.reset()

            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": [DISPLAY_NAME]}]))

        if cmd == "ReceivedItems":
            # args["index"] is the next empty index of the list of items the player has.
            asyncio.create_task(self.handle_received_items(args["index"], args["items"]))

        elif cmd == "Retrieved":

            # Last received item index from the server.
            if self.custom_data_keys_list[0] in args["keys"]:
                self.retrieved_last_item_id = True
                if not args["keys"][self.custom_data_keys_list[0]] is None:
                    self.last_received_item_index_server = args["keys"][self.custom_data_keys_list[0]]
                    print(self.last_received_item_index_server)
                else:
                    self.last_received_item_index_server = -1

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

        elif cmd == "Bounced": # DeathLink and RingLink updates
            tags = args.get("tags", [])

            if "DeathLink" in tags and self.last_death_link != args["data"]["time"]:
                self.last_death_link = args["data"]["time"]
                self.on_deathlink(args["data"])

            if "RingLink" in tags and self.ring_link_id != None:
                self.last_ring_link = args["data"]["time"]
                self.on_ringlink(args["data"])
        
        # TODO, I don't know if SetReply is the best option for this considering it will send stuff to other players
        # but it's the best idea I had in mind for now so it will be here for now.
        if cmd == "SetReply": # Ensure that the last item index received has been updated.
            if args["key"] == self.custom_data_keys_list[0] and args["slot"] == self.slot:
                self.data_sent = True
                print("Last item received index has been updated.")

    async def send_victory(self) -> None:
        await self.send_msgs([{"cmd": 'StatusUpdate', "status": 30}])

    async def get_custom_data_from_server(self):
        """
        Request custom data upon client initialization.
        """
        await self.send_msgs([{"cmd": "Get", "keys": [self.custom_data_keys_list[0]]}])

    async def update_last_item_id(self):
        """
        Send the new last received item ID to the server.
        """
        self.data_sent = False

        # Send new ending index to the sever
        index_msg = [{"cmd": "Set",
                      "key": self.custom_data_keys_list[0],
                      "want_reply": True,
                      "default": 0,
                      "operations": [{"operation": "replace", "value": self.last_received_item_index_server}]
                      }]
        await self.send_msgs(index_msg)
        asyncio.create_task(confirm_data_sent())

    async def confirm_data_sent(self):
        """
        Mini loop which checks if a SetReply has been sent back.
        If not, resend the Set command in order to ensure that the server has received it.
        """
        while(True):
            await asyncio.sleep(5)
            if data_sent: # Received SetReply so we can leave just fine.
                break
            else: # Seems the server did not get the command. Resend it.
                index_msg = [{"cmd": "Set",
                        "key": self.custom_data_keys_list[0],
                        "want_reply": True,
                        "default": 0,
                        "operations": [{"operation": "replace", "value": self.last_received_item_index_server}]
                        }]
                await self.send_msgs(index_msg)

    async def update_locations_checked(self):
        """
        All checking required to update locations the player has found.
        """
        #self.location_semaphore_in_use = True

        new_locations = []

        # Stage-related Locations
        for id, map in self.stage_location_mappings.items():
            if self.handler.isBossBeaten(*map) and id not in self.previous_location_checked:
                print("new location")
                new_locations.append(id)

        # New cards purchased
        for id, card_id in self.location_id_to_card_id.items():
            
            if id not in self.previous_location_checked and self.handler.hasCardBeenPurchased(card_id):
                new_locations.append(id)

        # Goal check
        for id, ending_map in self.location_id_to_ending_mapping.items():
            if id not in self.previous_location_checked and self.handler.isGoalCompleted(*ending_map):
                self.handler.setGoalCompleted(*ending_map)
                new_locations.append(id)

        # If there are any new locations, add them to the list and send them to the server.
        if new_locations:
            self.previous_location_checked += new_locations
                
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

        #self.location_semaphore_in_use = False

    async def update_magatama_and_blank_card(self):
        """
        Upon receiving items, we check if the new card count allows for the Sky-Blue Magatama or Blank Card
        to be unlocked.
        """
        #self.location_semaphore_in_use = True
        new_locations = []

        if (self.magatama_id not in self.previous_location_checked and 
            self.options["magatama_req"] <= self.handler.get_unlocked_card_count()):
            new_locations.append(self.magatama_id)

        if (self.blank_card_id not in self.previous_location_checked and
            self.options["blank_card_req"] <= self.handler.get_unlocked_card_count()):
            new_locations.append(self.blank_card_id)

        if new_locations:
            self.previous_location_checked += new_locations
            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

        #self.location_semaphore_in_use = False


    def on_deathlink(self, data: typing.Dict[str, typing.Any]) -> None:
        """
        Method that is called when a Deathlink is received.
        """
        self.waiting_for_deathlink = True

        return super().on_deathlink(data)

    async def send_deathlink(self):
        """
        Send deathlink to the server if server is active.
        """
        # Don't send anything if deathlink is not enabled.
        if not self.deathlink_enabled: return

        death_link_message = get_death_link_message(self.deathlink_trigger)
        await self.send_death(f"{self.player_names[self.slot]} {death_link_message}")


    def on_ringlink(self, data: typing.Dict[str, typing.Any]) -> None:
        """
        Method that is called when a Ring Link is received.
        """

        # Ring link can only be received when in stage.
        if self.checked_if_owns_stage:
            # Ensure that the ring link was not from ourselves.
            if data["source"] != self.ring_link_id:
                self.handler.addFunds(data["amount"])
                self.last_funds = self.handler.getFunds()

    def set_ring_link_tag(self, active: bool):
        """
        Updates Ring Link tag and sends said update to the server.
        """
        if active:
            self.tags.add("RingLink")
            self.ring_link_is_active = True
        else:
            self.tags.remove("RingLink")
            self.ring_link_is_active = False
        asyncio.create_task(self.send_msgs([{"cmd": "ConnectUpdate", "tags": self.tags}]))

    '''
    Handling Item List
    '''

    async def handle_received_items(self, network_index, network_items_list):
        """
        Handles all received items.
        Sends the latest item ID to the server and organizes the rest into queues to be used.
        """
        # When network_index = 0, it contains all items given to the client.
        id_list = [network_item.item for network_item in network_items_list]
        
        local_list_length = len(self.all_received_items)
        new_items_list: list[NetworkItem] = []

        # You'd want to be in the game and know the previous last index if you are to receive stuff.
        while (self.handler is None or self.handler.gameController is None) or not self.retrieved_last_item_id:
            print("waiting for the game and server reply")
            await asyncio.sleep(0.5)

        # You have no items acquired but have had some in a previous session.
        if (not self.all_received_items or self.all_received_items == []) and self.last_received_item_index_server > 0:
            local_list_length = self.last_received_item_index_server

        # All items the player has received are here
        if network_index <= 0:
            # Some desync has occurred between the server and client.
            if len(network_items_list) < local_list_length:
                logger.info("Error: Client has more items than the server's received item list")
                self.all_received_items = []
            new_items_list = network_items_list

        else: # Network index is not 0, new items
            if local_list_length == network_index:
                new_items_list = network_items_list
            # A desync has occurred
            else:
                logger.info("Error: Desync between client and server items has occurred")
                sync_msg = [{"cmd": "Sync"}]
                if self.locations_checked:
                    sync_msg.append({"cmd": "LocationChecks",
                                     "locations": list(self.locations_checked)})
                await self.send_msgs(sync_msg)

        if len(new_items_list) <= 0: return

        self.handle_items(new_items_list, network_index)

        # Check for Magatama and Blank Card
        '''
        while (self.location_semaphore_in_use):
            await asyncio.sleep(0.5)
        '''
        await self.update_magatama_and_blank_card()

        # Update last used index.
        await self.add_to_item_list(new_items_list)

    def handle_items(self, item_list, network_index):
        """
        Organizes all received items properly into their queues.
        """
        if len(item_list) <= 0: return

        for i in range(len(item_list)):
            item_id = item_list[i].item
            if item_id in PERMANENT_ITEMS:
                self.permanent_item_queue.append(item_id)
            elif item_id in ITEM_ID_TO_CARD_ID:
                self.card_item_queue.append(item_id)
            # We do not want to repeat stage-only items each reset such as traps.
            elif item_id in STAGE_ONLY_ITEMS and network_index + i >= self.last_received_item_index_server:
                self.game_item_queue.append(item_id)

        self.handle_card_items()
        self.handle_permanent_items()

    def handle_card_items(self):
        """
        Adds cards to the unlocked list. 
        """
        card_id = 0

        for card_item in self.card_item_queue:
            card_id = ITEM_ID_TO_CARD_ID.get(card_item, -1)
            if card_id == -1:
                logger.info("Error: Card ID does not exist")
                continue
            
            self.handler.receiveCard(card_id)
  
            if not card_id in ITEM_CARDS:
                self.handler.setCardUnlockState(card_id, True)
            
            self.handler.add_to_unlocked_card_count()

            self.handler.setCardIcon(card_id)
            
        self.card_item_queue = []

        if self.options["goal"] == GOAL_ITEMS or self.options["goal"] == GOAL_ALL:
            self.check_victory()
        
    def handle_permanent_items(self):
        """
        These items can be processed anywhere at any time. The vast majority of them.
        """
        for item_id in self.permanent_item_queue:
            match item_id:
                case 1:
                    self.handler.addInitialLives()
                case 2:
                    self.handler.addInitialBombs()
                case 3:
                    self.handler.addContinues()
                case 4:
                    self.handler.lowerDifficulty()
                case 5:
                    self.handler.addCardSlots()
                    self.handler.setCardSlotCount(self.handler.getHandlerCardSlotCount())
                case 12:
                    self.handler.addMaxLives()
                case 13:
                    self.handler.addMaxBombs()
                case 100:
                    self.handler.unlock_character(CHARACTER_REIMU)
                case 101:
                    self.handler.unlock_character(CHARACTER_MARISA)
                case 102:
                    self.handler.unlock_character(CHARACTER_SAKUYA)
                case 103:
                    self.handler.unlock_character(CHARACTER_SANAE)
                case 200:
                    self.handler.addStage()
                case 201:
                    self.handler.addStage(CHARACTER_REIMU)
                case 202:
                    self.handler.addStage(CHARACTER_MARISA)
                case 203:
                    self.handler.addStage(CHARACTER_SAKUYA)
                case 204:
                    self.handler.addStage(CHARACTER_SANAE)
                case 205:
                    self.handler.unlock_extra()
                case 206:
                    self.handler.unlock_extra(CHARACTER_REIMU)
                case 207:
                    self.handler.unlock_extra(CHARACTER_MARISA)
                case 208:
                    self.handler.unlock_extra(CHARACTER_SAKUYA)
                case 209:
                    self.handler.unlock_extra(CHARACTER_SANAE)
                case 600:
                    self.handler.setGoalCompleted(CHARACTER_REIMU, GOAL_CHIMATA)
                case 601:
                    self.handler.setGoalCompleted(CHARACTER_MARISA, GOAL_CHIMATA)
                case 602:
                    self.handler.setGoalCompleted(CHARACTER_SAKUYA, GOAL_CHIMATA)
                case 603:
                    self.handler.setGoalCompleted(CHARACTER_SANAE, GOAL_CHIMATA)
                case 604:
                    self.handler.setGoalCompleted(CHARACTER_REIMU, GOAL_CHIMATA_BLANK)
                case 605:
                    self.handler.setGoalCompleted(CHARACTER_MARISA, GOAL_CHIMATA_BLANK)
                case 606:
                    self.handler.setGoalCompleted(CHARACTER_SAKUYA, GOAL_CHIMATA_BLANK)
                case 607:
                    self.handler.setGoalCompleted(CHARACTER_SANAE, GOAL_CHIMATA_BLANK)
                case 608:  
                    self.handler.setGoalCompleted(CHARACTER_REIMU, GOAL_MOMOYO)
                case 609:
                    self.handler.setGoalCompleted(CHARACTER_MARISA, GOAL_MOMOYO)
                case 610:
                    self.handler.setGoalCompleted(CHARACTER_SAKUYA, GOAL_MOMOYO)
                case 611:
                    self.handler.setGoalCompleted(CHARACTER_SANAE, GOAL_MOMOYO)  

            self.permanent_item_queue = []

            # Could be a victory condition.
            if item_id >= 600 and item_id <= 612:
                self.check_victory()

    async def add_to_item_list(self, item_list: list[NetworkItem]):
        """
        Add to the total list of items and send the new last index to the server.
        """
        item_id_list: list[int] = []

        for new_item in item_list:
            item_id_list.append(new_item.item)

        self.all_received_items += item_id_list

        #print(f"init - {self.last_received_item_index_server}")

        self.last_received_item_index_server = len(self.all_received_items)

        #print(f"now - {self.last_received_item_index_server}")

        asyncio.create_task(self.update_last_item_id())

    def check_victory(self) -> None:
        """
        Check the handler to see if the player has achieved all conditions to win.
        If so, send the signal to Archipelago.
        """
        goal_condition = self.options["goal"]
        characters_needed = self.options["ending_req"]
        cards_needed = self.options["card_req"]

        chimata_index = 0
        momoyo_index = 0
        chimata_alt_index = 0
        card_count = 0

        chimata_victory = False
        momoyo_victory = False
        chimata_alt_victory = False
        card_count_victory = False

        achieved_victory = False

        if goal_condition == GOAL_CHIMATA or goal_condition == GOAL_ALL:
            for character in CHARACTERS:
                if self.handler.endingCompleted[character]:
                    chimata_index += 1
            if chimata_index >= characters_needed:
                achieved_victory = True
                chimata_victory = True
        
        if goal_condition == GOAL_MOMOYO or goal_condition == GOAL_ALL:
            for character in CHARACTERS:
                if self.handler.extraCompleted[character]:
                    momoyo_index += 1
            if momoyo_index >= characters_needed:
                achieved_victory = True
                momoyo_victory = True
        
        if goal_condition == GOAL_CHIMATA_BLANK or goal_condition == GOAL_ALL:
            for character in CHARACTERS:
                if self.handler.altEndingCompleted[character]:
                    chimata_alt_index += 1
            if chimata_alt_index >= characters_needed:
                achieved_victory = True
                chimata_alt_victory = True
        
        if goal_condition == GOAL_ITEMS or goal_condition == GOAL_ALL:
            card_count = self.handler.get_unlocked_card_count()
            if card_count >= cards_needed:
                achieved_victory = True
                card_count_victory = True
        
        if goal_condition == GOAL_ALL:
            achieved_victory = chimata_victory and chimata_alt_victory and card_count_victory
            if self.options["extra_stage"] != EXTRA_NOT_INCLUDED:
                achieved_victory = achieved_victory and momoyo_victory

        if achieved_victory:
            print("Sending victory")
            asyncio.create_task(self.send_victory())

    '''
    Async Loops
    '''

    async def game_loop(self):
        """
        The main loop that handles giving stage resources and updating boss-related locations
        along all details from the shop.
        Stuff that happens while in-stage.
        """
        try:
            
            print("Game Loop Init")

            difficulty_check = self.options["difficulty_check"]
            lower_difficulty_check = self.options["check_mult_difficulties"]

            boss_present = False
            boss_counter = -1
            given_resources = False

            new_lives = 0
            current_lives = 0

            new_bombs = 0
            current_bombs = 0

            current_score = 0
            current_continue = 0
            previous_stage = 0
            current_stage = 0
            current_character = None

            currently_in_stage = True

            impossible_state = False
            spell_practice = False
            game_mode = None

            time_in_stage = 0
            game_state = -1

            initial_loop_buffer = True

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

                        # Spellcard practice
                        game_mode = self.handler.get_game_mode()
                        # I don't know why ZUN chose these numbers in specific.
                        # This ignores checks (and kicking the player out) on spellcard practice and the demos.
                        if game_mode == 32 or game_mode == 36 or game_mode == 64: 
                            await asyncio.sleep(2)
                            continue

                        currently_in_stage = True
                        boss_counter = -1
                        boss_present = False
                        impossible_state = False
                        current_score = self.handler.getScore()
                        current_continue = self.handler.getContinues()
                        current_stage = self.handler.getStage()

                        # There is dialogue at the end of stage 5 so we need to wait until that is over and stage 6 has begun.
                        while current_stage == 5 and self.handler.getTimeInStage() > 2000:
                            await asyncio.sleep(1)
                        if current_stage == 5:
                            await asyncio.sleep(1.5)
                            current_stage = self.handler.getStage()

                        # The client will crash since it changes stages in code before loading in the GUI so we wait.
                        if current_stage == 6:
                            await asyncio.sleep(2)
                        
                        self.handler.updateCardLockState()

                        # There is a shop in the middle of the extra stage so we need to account for it.
                        # If you manage to somehow have less than 100,000 score upon reaching Momoyo, you deserve it.
                        if current_stage == 7 and current_score > 10000:
                            boss_counter = 0
                        # New game or extra stage
                        elif current_stage == 1 or current_stage == 7:
                            
                            self.handler.setGameCardUnlockStates()

                            # Incase the player dies with 0 score, it will still recognize a restart
                            self.handler.setScore(1) 
                            current_character = self.handler.getCurrentCharacter()
                            given_resources = False
                            previous_stage = 0

                            if current_stage == 1: self.handler.setContinues(self.handler.continues)
                            

                    # This specific block is for if the player restarts the game or uses a continue.
                    if not given_resources:
                        while not self.handler.guiExists():
                            await asyncio.sleep(0.5)
                        
                        self.handler.setLives(self.handler.initial_lives)
                        self.handler.setBombs(self.handler.initial_bombs)

                        given_resources = True
                        
                        current_lives = self.handler.getLives()

                    
                    # Allow the game to fully load the stage first.
                    # If the client attempts to force the player back while the stage is loading the game will crash.
                    if not self.checked_if_owns_stage and previous_stage != current_stage:
                        print("h")

                        # The stage updates before the time so we need a slight buffer just in case.
                        if initial_loop_buffer:
                            print("need to wait")
                            initial_loop_buffer = False
                            await asyncio.sleep(1)

                        time_in_stage = self.handler.getTimeInStage()
                        if time_in_stage >= 120:
                            previous_stage = current_stage
                            self.checked_if_owns_stage = True

                            if current_stage == None or current_character == None:
                                current_character = self.handler.getCurrentCharacter()
                                current_stage = self.handler.getStage()
                            # If the current stage is not unlocked, send the player back.
                            if not self.handler.isStageUnlocked(current_character, current_stage):
                                impossible_state = True
                            # Player snuck in with a character they don't own.
                            if not self.handler.isCharacterUnlocked(current_character):
                                logger.info("Error: Character is not unlocked. Going back to Main Menu")
                                impossible_state = True
                            # Player snuck in with a difficulty that has not been unlocked yet.
                            if not self.handler.isDifficultyUnlocked(self.handler.getDifficulty()):
                                logger.info("Error: Difficulty is not unlocked. Going back to Main Menu")
                                impossible_state = True
    
                            if impossible_state:
                                self.handler.forceToMainMenu()
                                self.checked_if_owns_stage = False

                    # Checking for continues and restarts.
                    if current_score > self.handler.getScore():
                        if current_continue > self.handler.getContinues():
                            # Player's score could have lowered due to using a continue.
                            current_score = self.handler.getScore()
                            current_continue = self.handler.getContinues()
                        else:
                            # Player has restarted the game.     
                            currently_in_stage = False
                            # This may seem unnecessary but it is for ringlink to know that you didn't suddenly lose all of your funds.
                            self.checked_if_owns_stage = False 
                            continue
                        given_resources = False
                    else: # Update Score
                        current_score = self.handler.getScore()

                    # Check if a boss appeared.
                    if not boss_present:
                        if self.handler.isBossActive():
                            boss_present = True
                            boss_counter += 1
                    else:
                        if boss_present:
                            # Boss slain.
                            if not self.handler.isBossActive():
                                print("boss down")
                                if not self.handler.isCurrentBossDefeated(boss_counter):
                                    print("new boss down")
                                    self.handler.setCurrentBossDefeated(boss_counter, difficulty_check, lower_difficulty_check)
                                    await self.update_locations_checked()
                                boss_present = False

                    # Did the player's lives change.
                    new_lives = self.handler.getLives()
                    if current_lives != new_lives:
                        if new_lives > self.handler.max_lives:
                            self.handler.setLives(self.handler.max_lives)
                            new_lives = self.handler.max_lives
                        # You died
                        if current_lives > new_lives:
                            if self.handler.initial_bombs < self.handler.max_bombs:
                                self.handler.setBombs(self.handler.initial_bombs)
                            else:
                                self.handler.setBombs(self.handler.max_bombs)
                        current_lives = new_lives

                    # Check if the player has more bombs than max.
                    new_bombs = self.handler.getBombs()
                    if current_bombs != new_bombs:
                        if new_bombs > self.handler.max_bombs:
                            self.handler.setBombs(self.handler.max_bombs)
                        current_bombs = new_bombs

                # Went to main menu or shop.
                elif currently_in_stage:
                    initial_loop_buffer = True
                    currently_in_stage = False
                    self.checked_if_owns_stage = False

        except Exception as e:
            logger.error(f"Stage ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def shop_loop(self):
        """
        The main loop for the shop.
        Handles purchasing cards and disabling cards that have already
        been purchased but not unlocked. 
        """
        try:

            # A basic variable for editing gotten values before setting them back.
            temp_value: int = 0
            
            currently_in_shop = False
            current_power = 0

            blank_card_state = False

            shop_card_list = []
            shop_card_id_list = []
            player_card_list = []
            
            new_card_list = []

            player_lives = 0
            player_bombs = 0

            game_state = -1

            print("Shop Loop Init")

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(0.5)

                game_state = self.handler.get_game_state()

                if game_state == -1:
                    continue
                
                '''Shop Check'''
                if game_state == IN_SHOP:
                    # Entering Shop
                    if not currently_in_shop:
                        
                        current_power = self.handler.getPower()
                        player_lives = self.handler.getLives()
                        player_bombs = self.handler.getBombs()

                        currently_in_shop = True
                        #logger.info("Entered a shop")
                        player_card_list = self.handler.getHeldCards()

                        if BLANK_CARD in player_card_list:
                            blank_card_state = True

                        # Disabling cards that have been purchased before but are not unlocked.
                        shop_card_list = self.handler.getShopCards()
                        shop_card_id_list = self.handler.shop_card_id_to_card_id(shop_card_list)
                        for i in range(len(shop_card_list)):   
                            if (self.handler.cardsPurchased[shop_card_id_list[i]] 
                            and not self.handler.cardsUnlocked[shop_card_id_list[i]]):
                                self.handler.disableCard(shop_card_list[i])

                # Leaving Shop    
                elif currently_in_shop:
                    #logger.info("Left a shop")
                    currently_in_shop = False
                    new_card_list = self.handler.getHeldCards()
                    card_addresses = self.handler.getCardAddresses()

                    # Undo the effects of Phoenix's Tail if you do not have it received.
                    if MOKOU_CARD in new_card_list:
                        if not self.handler.hasCardBeenReceived(MOKOU_CARD):
                            self.handler.setLives(player_lives)
                            self.handler.setCardUnlockState(MOKOU_CARD, False) 

                    if blank_card_state: # Owned Blank Card
                        for card in new_card_list:
                            if not self.handler.hasCardBeenPurchased(card):
                                self.handler.purchaseCard(card)

                            if not self.handler.hasCardBeenReceived(card):
                                self.handler.setCardUnlockState(card, False)
                    elif len(new_card_list) != len(player_card_list): # Didn't own blank card but got a new card.
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
                        # Life and Bomb items will edit the GUI so we want it to exist before messing with them.
                        while not self.handler.guiExists():
                            await asyncio.sleep(0.5)
                            
                        if (not self.handler.hasCardBeenPurchased(LIFE_CARD) 
                        and self.handler.getCardUnlockedState(LIFE_CARD)): 
                            self.handler.purchaseCard(LIFE_CARD)
                            if not self.handler.hasCardBeenReceived(LIFE_CARD):
                                self.handler.setLives(player_lives)
                                self.handler.setCardUnlockState(LIFE_CARD, False) 

                        if (not self.handler.hasCardBeenPurchased(BOMB_CARD) 
                        and self.handler.getCardUnlockedState(BOMB_CARD)): 
                            self.handler.purchaseCard(BOMB_CARD)
                            if not self.handler.hasCardBeenReceived(BOMB_CARD):
                                self.handler.setBombs(player_bombs)
                                self.handler.setCardUnlockState(BOMB_CARD, False) 

                        if (not self.handler.hasCardBeenPurchased(NAZRIN_CARD) 
                        and self.handler.getCardUnlockedState(NAZRIN_CARD)): 
                            self.handler.purchaseCard(NAZRIN_CARD)
                            if not self.handler.hasCardBeenReceived(NAZRIN_CARD):
                                self.handler.addFunds(-50)
                                self.handler.setCardUnlockState(NAZRIN_CARD, False) 

                        if (not self.handler.hasCardBeenPurchased(RINGO_CARD) 
                        and self.handler.getCardUnlockedState(RINGO_CARD)):
                            self.handler.purchaseCard(RINGO_CARD)
                            if not self.handler.hasCardBeenReceived(RINGO_CARD):
                                self.handler.setPower(current_power)
                                self.handler.setCardUnlockState(RINGO_CARD, False) 

                    # Sannyo's card is weird in the fact that it's effect is only active if you have a card of its ID
                    # when you start a stage. To account for this, we have to change it before the stage starts.
                    # I chose the life card since it cannot be owned as a permanent card so this wouldn't make
                    # a card you have on you into a Dragon Pipe.
                    for i in range(len(new_card_list)):
                        if new_card_list[i] == SANNYO_CARD and not self.handler.hasCardBeenReceived(SANNYO_CARD):
                            self.handler.setCardID(card_addresses[i], LIFE_CARD)
                        elif new_card_list[i] == LIFE_CARD and self.handler.hasCardBeenReceived(SANNYO_CARD):
                            self.handler.setCardID(card_addresses[i], SANNYO_CARD)
                    
                    await self.update_locations_checked()

                    blank_card_state = False
        except Exception as e:
            logger.error(f"Shop ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def menu_loop(self):
        """
		Loop for dealing with main menu stuff.
        Mostly preventing you from going to places you should not be.
		"""
        print("Menu Loop Init")

        try:
            MAIN_MENU_SELECT = 1
            DIFFICULTY_SELECT = 5
            CHARACTER_SELECT = 6
            SPELLCARD_PRACTICE_SELECT = 18
            SPELLCARD_PRACTICE2_SELECT = 19
            SPELLCARD_PRACTICE3_SELECT = 20

            game_state = -1
            menu_select_state = None
            selected_difficulty = None
            default_difficulty = DIFFICULTY_LUNATIC if not self.options["exclude_lunatic"] else DIFFICULTY_HARD

            previous_character = 0
            current_character = None

            previous_difficulty = DIFFICULTY_LUNATIC if not self.options["exclude_lunatic"] else DIFFICULTY_HARD
            current_difficulty = None

            new_locations = []

            current_menu_state = None

            currently_in_menu = False

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(0.5)

                game_state = self.handler.get_game_state()

                if game_state == IN_MENU:
                    # Entered the menu or just connected to the game.
                    if not currently_in_menu:
                        #logger.info("Entered main menu")

                        new_locations = []
                        self.able_to_check = True
                        currently_in_menu = True  

                        # If a card has been received, make it show in the main menu.
                        # Also locks cards that you have in your inventory despite not being given to you.
                        self.handler.setDefaultCardUnlockStates()

                        # Set extra stage for every character depending on whether you have them unlocked or not.
                        # You also need the Sky-Blue Magatama.
                        for character in CHARACTERS:
                            if self.handler.hasCardBeenReceived(MAGATAMA_CARD):
                                self.handler.set_extra_stage_unlock(character, self.handler.get_extra_unlock_status(character))
                            else:
                                self.handler.set_extra_stage_unlock(character, False)

                        '''
                        Additional Location Check upon entering the menu.
                        '''   
                        # We shouldn't check locations until they are all already added to the list.
                        # That could be some scary read-write issues.
                        '''
                        while(self.location_semaphore_in_use):
                            print("Location semaphore in use")
                            await asyncio.sleep(0.5)
                        '''

                        # Extra goal check just in-case that it did not properly register.
                        for id, ending_map in self.location_id_to_ending_mapping.items():
                            if id not in self.previous_location_checked and self.handler.isGoalCompleted(*ending_map):
                                print("new location!!!")
                                self.handler.setGoalCompleted(*ending_map)
                                new_locations.append(id)

                        if self.options["goal"] == GOAL_ITEMS or self.options["goal"] == GOAL_ALL:
                            if self.options["card_req"] <= self.handler.get_unlocked_card_count():
                                self.check_victory()
        
                        # If we actually found something new then send it.
                        if new_locations:
                            print("Missed something it seems")
                            print(f"{new_locations}")
                            self.previous_location_checked += new_locations
                            await self.send_msgs([{"cmd": 'LocationChecks', "locations": new_locations}])

                    # General Main Menu Stuff.
                    menu_select_state = self.handler.getMainMenuSelectArea()

                    if menu_select_state == CHARACTER_SELECT:
                        selected_difficulty = self.handler.getDifficulty()

                        # Lock character options
                        if current_menu_state != CHARACTER_SELECT:
                            current_menu_state = CHARACTER_SELECT
                            if selected_difficulty != 4: # Don't lock on extra select
                                self.handler.setCharacterRestrict()

                        
                        # Player entered a difficulty they do not have access to, fix it.
                        if not self.handler.isDifficultyUnlocked(selected_difficulty):
                            logger.info(f"""Error: Entered locked difficulty option. Defaulting to {DIFFICULTY_NAMES[default_difficulty]}""")
                            self.handler.setDifficulty(default_difficulty) 
                    elif menu_select_state == DIFFICULTY_SELECT:

                        # Lock difficulty options
                        if current_menu_state != DIFFICULTY_SELECT:
                            current_menu_state = DIFFICULTY_SELECT
                            self.handler.setDifficultyRestrict()         
                    elif menu_select_state == MAIN_MENU_SELECT:
                        if current_menu_state != MAIN_MENU_SELECT:
                            current_menu_state = MAIN_MENU_SELECT
                            self.handler.setPracticeRestrict()
                    elif menu_select_state == SPELLCARD_PRACTICE_SELECT or menu_select_state == SPELLCARD_PRACTICE2_SELECT:
                        if current_menu_state != SPELLCARD_PRACTICE_SELECT:
                            current_menu_state = SPELLCARD_PRACTICE_SELECT
                            self.handler.setSpellCardPracticeRestrict()
                    else:
                        if current_menu_state != None:
                            current_menu_state = None

                elif currently_in_menu:
                    current_menu_state = None
                    currently_in_menu = False

                    # Since unlock state is a factor in determining whether you've purchased an item card, disable in stage if not purchased.
                    for item_card in ITEM_CARDS:
                        if not self.handler.hasCardBeenPurchased(item_card):
                            print(f"{item_card} not purchased")
                            self.handler.setCardUnlockState(item_card, 0)

        except Exception as e:
            logger.error(f"Main Menu ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def stage_item_loop(self):
        """
        Loop that handles items that can only be processed while in-stage.
        """
        try:
            freeze_duration = 2
            freeze_timer = 0

            increased_speed_duration = 5
            increased_speed_timer = 0

            inverse_speed_duration = 5
            inverse_speed_timer = 0

            reduced_damage_duration = 3
            reduced_damage_timer = 0

            game_state = -1
            currently_in_menu = False

            while not self.exit_event.is_set() and self.handler and not self.in_error:
                await asyncio.sleep(1.0)

                # Wait until the player is actively in a stage they can play fully.
                if self.checked_if_owns_stage:

                    for item_id in self.game_item_queue:
                        match item_id:
                            case 8:
                                self.handler.addFunds(100)
                            case 9:
                                self.handler.addPower(50)
                            # Filler
                            case 400:
                                self.handler.addFunds(10)
                            case 401:
                                self.handler.addFunds(25)
                            case 402:
                                self.handler.addPower(1)
                            case 403:
                                self.handler.addPower(10)
                            case 404:
                                self.handler.addLifeFrags(1)
                            case 405:
                                self.handler.addBombFrags(1)
                            # Traps
                            case 500:
                                self.handler.setSpeed([0, 0])
                                freeze_timer = freeze_duration
                            case 501:
                                self.handler.setSpeed([1000, 500])
                                increased_speed_timer = increased_speed_duration
                            case 502:
                                print("Trap: Forced to fight Seija")
                                self.handler.setSpeed([-CHARACTER_SPEEDS[self.handler.getCurrentCharacter()][0],
                                                       -CHARACTER_SPEEDS[self.handler.getCurrentCharacter()][1]])
                                inverse_speed_timer = inverse_speed_duration
                            case 503:
                                self.handler.addFunds(-10)
                            case 504:
                                self.handler.addFunds(-50)
                            case 505:
                                self.handler.addFunds(-100)
                            case 506:
                                self.handler.addPower(-25)    
                            case 507:
                                self.handler.addPower(-50)  
                            # Would be the weakness trap but it is not implemented right now.
                            case 509:
                                self.handler.killPlayer()
                
                    # Since asyncio only stops the coroutine at await, this won't mess with the list while it is being filled.
                    self.game_item_queue = []

                    if freeze_timer == 0:
                        self.handler.resetSpeed()
                    elif increased_speed_timer == 0:
                        self.handler.resetSpeed()
                    elif inverse_speed_timer == 0:
                        self.handler.resetSpeed()

                    freeze_timer -= 1
                    increased_speed_timer -= 1
                    inverse_speed_timer -= 1
                    reduced_damage_timer -= 1

        except Exception as e:
            logger.error(f"Stage Item ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def death_link_loop(self):
        """
        Loop that handles death link.
        """
        print("death link loop init")
        try:
            active_deathlink = False
            entered_stage = False
            current_lives = 0
            deathlink_counter = 0

            while not self.exit_event.is_set() and self.handler and not self.in_error:   
                if self.deathlink_enabled:
                    await asyncio.sleep(1)
                else: # Can't engage in deathlink if it is not enabled.
                    await asyncio.sleep(5)
                    continue
  
                # Actively in a stage that is owned by the player.
                if self.checked_if_owns_stage:
                    if not entered_stage:
                        current_lives = self.handler.getLives()
                        entered_stage = True

                    # Only kill the player when a deathlink is available and the player is currently not dead.
                    if self.waiting_for_deathlink and self.handler.getPlayerState() == 1:
                        self.handler.killPlayer()
                        self.died_to_deathlink = True
                    
                    if current_lives != self.handler.getLives():
                        # Player died
                        if current_lives > self.handler.getLives():
                            # Deathlink deaths do not count towards the counter.
                            if self.died_to_deathlink:
                                self.died_to_deathlink = False
                                self.waiting_for_deathlink = False
                                current_lives = min(self.handler.getLives(), self.handler.max_lives)    
                                continue

                            # Game Over has lives set to -1 for some reason.
                            if (self.deathlink_trigger == DEATHLINK_TRIGGER_LIFE or 
                               (self.deathlink_trigger == DEATHLINK_TRIGGER_GAMEOVER and current_lives == -1)):
                                deathlink_counter += 1

                                # Send the deathlink to your poor and unfortunate friends.
                                if deathlink_counter >= self.deathlink_amnesty:
                                    deathlink_counter = 0
                                    await self.send_deathlink() 
                                else:
                                    logger.info(f"DeathLink: {deathlink_counter}/{self.deathlink_amnesty}")

                        # Kind of a bandage fix for the client loading lives before I can set them to max_lives but it works.
                        current_lives = min(self.handler.getLives(), self.handler.max_lives)    
                else:
                    entered_stage = False
        except Exception as e:
            logger.error(f"DeathLink ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

    async def ring_link_loop(self):
        """
        Loop that handles ring link.
        """
        print("ring link loop init")
        try:
            active_ringlink = False
            current_funds = 0
            self.last_funds = -1
            funds_difference = 0

            self.ring_link_id = f"{str(self.team)}_{str(self.slot)}_RingLinkTH18"
            
            while not self.exit_event.is_set() and self.handler and not self.in_error:   
                if self.ring_link_enabled:
                    await asyncio.sleep(1.5)
                else: # Can't engage in ringlink if it is not enabled.
                    await asyncio.sleep(5)
                    self.last_funds = -1
                    continue

                if self.checked_if_owns_stage:
                    current_funds = self.handler.getFunds()

                    if self.last_funds == -1:
                        await asyncio.sleep(1)
                        self.last_funds = current_funds
                        continue

                    if self.last_funds != current_funds:
                        funds_difference = current_funds - self.last_funds
                        self.last_funds = current_funds
                        asyncio.create_task(self.send_msgs([{"cmd": "Bounce", "tags": ["RingLink"], "data": {"amount": funds_difference, "source": self.ring_link_id, "time": time.time()}}]))
                else:
                    self.last_funds = -1

                
        except Exception as e:
            logger.error(f"RingLink ERROR: {e}")
            logger.error(traceback.format_exc())
            self.in_error = True

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

        else:
            # Receive server data
            if not ctx.retrieved_last_item_id:
                try:
                    print("Getting previously collected items from server.")
                    await ctx.get_custom_data_from_server()
                except:
                    ctx.inError = True
                    logger.error("Failed to retrieve save data.")
                    logger.error(traceback.format_exc())

        # Connecting to the game
        if ctx.handler == None and not ctx.in_error:
            logger.info(f"Connecting to {SHORT_NAME}...")
            asyncio.create_task(ctx.connect_to_game())
            while(ctx.handler == None and not ctx.exit_event.is_set()):
                await asyncio.sleep(1)

        # Error check, try to reconnect to the game.
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

        logger.info("Beginning main loops")
        client_loops = []
        client_loops.append(asyncio.create_task(ctx.game_loop()))
        client_loops.append(asyncio.create_task(ctx.menu_loop()))
        client_loops.append(asyncio.create_task(ctx.shop_loop()))
        client_loops.append(asyncio.create_task(ctx.stage_item_loop()))
        client_loops.append(asyncio.create_task(ctx.death_link_loop()))
        client_loops.append(asyncio.create_task(ctx.ring_link_loop()))

        # Update any locations made before the connection.

        await ctx.update_locations_checked()

        if ctx.options["deathlink"]:
            ctx.deathlink_enabled = True
            await ctx.update_death_link(True)

        ctx.deathlink_trigger = ctx.options["deathlink_trigger"]  

        ctx.deathlink_amnesty = ctx.options["deathlink_amnesty"]

        if ctx.options["ring_link"]:
            ctx.ring_link_enabled = True
            ctx.set_ring_link_tag(True)

        if ctx.options["exclude_lunatic"]:
            ctx.handler.excludeLunatic()

        # Initial maximum lives and bombs
        ctx.handler.setMaxLives(ctx.options["init_max_lives"])
        ctx.handler.setMaxBombs(ctx.options["init_max_bombs"])

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