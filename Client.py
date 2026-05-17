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

        self.item_id_to_name = None
        self.item_name_to_id = None
        self.location_id_to_name = None
        self.location_name_to_id = None

        self.options = None
        self.in_error = None
        self.is_game_running: bool = False
        self.is_connected: bool = False
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

        self.is_connected = False
        self.is_game_running = False

        self.all_location_ids = []
        self.previous_location_checked = []
        self.handler = None

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

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        """
        Manage packages received from the server
        This is the big one.
        """
        if cmd == "RoomInfo":
            print("a")

        if cmd == "Connected":
            self.is_connected = True

        if cmd == "ReceivedItems":
            print("new")
        elif cmd == "Retrieved":
            print("new")

        elif cmd == "DataPackage":
            print("new")

        elif cmd == "Bounced":
            print("cool")
        
        if cmd == "SetReply":
            print("g")


    def client_received_initial_server_data(self) -> bool:
        """
        If this method returns true then:
            - All LocationInfo packages have been received
            - DataPackage package received (id_to_name maps and name_to_id maps populated)
            - Connection package received (slot number populated)
            - RoomInfo package received (seed name populated)
        """
        return self.is_connected  

    def check_victory(self) -> bool:
        print("soon")

    async def handle_received_items(self, network_index, network_items_list):
        print("soon")

    

    '''
    Async Loops
    '''

    async def wait_for_initial_connection_info(self):
        """
        Waits until the client has finished the initial conversation with the server.
        """
        if self.client_received_initial_server_data():
            return
        
        logger.info("Waiting for a connection from the server...")
        while not self.client_received_initial_server_data() and not self.exit_event_is_set():
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

    async def main_loop(self):
        """
        The main loop that handles giving resources and updating locations.
        """
        try:
            boss_present - False
            current_lives = 0
            boss_counter = -1
            resources_given = False
            no_check = True
            current_score = 0
            current_continue = 0
            print("h")
            while not self.exit_event.is_set() and self.handler and not self.inError:
                await asyncio.sleep(0.5)
                if self.handler.inStage:
                    print("a")
                else:
                    print("g")
                
        except Exception as e:
            logger.error(f"Main ERROR: {e}")
            logger.error(traceback.format_exc())
            self.inError = True

    async def menu_loop(self):
        """
		Loop that handles the characters lock and difficulty lock, depending on the menu.
		Also handle starting item from options
		"""
        print("new")

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

    async def update_locations_checked(self):
        print("soon")

    async def game_watcher(ctx):
        """
        The main client loop which watches the gameplay process.
        If connection is lost, it will reconnect.
        """
        # ctx is the Context Client Instance

        await ctx.wait_for_intial_connection_info()
       # await ctx.initial_load_last_item_list()

        while not ctx.exit_event.is_set():
            # Client disconnected from the server.
            if not ctx.server:
                logger.info("Disconnected from server, trying to reconnect...")
                ctx.reset()
                await ctx.wait_for_initial_connection_info()
            
            if ctx.handler == None and not ctx.inError:
                logger.info(f"Connecting to {SHORT_NAME}...")
                asyncio.create_task(ctx.connect_to_game())
                while(ctx.handler == None and not ctx.exit_event_is_set()):
                    await asyncio.sleep(1)

            if ctx.inError:
                logger.info(f"An error has broken connection. Waiting for connection to {SHORT_NAME}")
                ctx.handler.gameController = None
                asyncio.create_task(ctx.reconnect_to_game())
                await asyncio.sleep(1)
                while(ctx.handler.gameController == None and not ctx.exit_event_is_set()):
                    await asyncio.sleep(1)

            if ctx.handler and ctx.handler.gameController:
                logger.info(f"{SHORT_NAME} process found. Beginning game loop.")
                ctx.inError = False

            client_loops = []
            loops.append(asyncio.create_task(ctx.main_loop()))
            loops.append(asyncio.create_task(ctx.menu_loop()))
            # Add more loops later

            await ctx.update_locations_checked()
            # Update Stage List

            # Death Link stuff

            # Edit handler as needed

            # If all is going well, we can just loop forever.
            while not ctx.exit_event.is_set() and ctx.server and not ctx.inError:
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