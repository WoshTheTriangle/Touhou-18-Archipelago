from worlds.AutoWorld import World
from worlds.LauncherComponents import Component, components, launch_subprocess, Type

from collections.abc import Mapping

from .WebWorld import TouhouUMWebWorld
from . import Items, Locations, Regions, Rules, Options as UMOptions
from .variables.meta_data import *

from typing import Any

def launch_client():
    from .Client import launch
    launch_subprocess(launch, name="GameClient")

components.append(Component(
    SHORT_NAME+" Client",
    "GameClient",
    func=launch_client,
    component_type=Type.CLIENT
))

class TouhouUMWorld(World):
    """
    Cool game. Toho roguelike.
    """
    game = DISPLAY_NAME

    web = TouhouUMWebWorld()

    item_name_to_id = Items.get_item_to_id_dict()
    location_name_to_id = Locations.location_table

    origin_region_name = "Menu"

    options_dataclass = UMOptions.Th18Options
    options: UMOptions.Th18Options

    # Manditory Arcipelago World methods    

    def generate_early(self) -> None:
        # Giving the player precollected items (player character and maybe some other stuff)
        self.push_precollected(self.create_item("Reimu"))

    def set_rules(self) -> None:
        Rules.set_all_rules(self)

    def create_regions(self) -> None:
        Regions.create_and_connect_regions(self)
        #Locations.create_all_locations(self)

    def create_items(self) -> None:
        Items.create_all_items(self)

    def create_item(self, name: str) -> Items.TouhouUMItem:
        return Items.create_item_with_correct_classification(self, name)

    def get_filler_item_name(self) -> str:
        return Items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        data = self.options.as_dict(
            "trap_chance", "stage_unlock", 
            "extra_stage", "magatama_req", 
            "blank_card_req", "goal", 
            "ending_req", "card_req", 
            "difficulty_check", "check_mult_difficulties", 
            "exclude_lunatic", "init_max_lives", 
            "max_life_item", "init_max_bombs", 
            "max_bomb_item", "deathlink", 
            "deathlink_trigger", "deathlink_amnesty"
        )
        return data
