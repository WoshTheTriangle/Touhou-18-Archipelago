from worlds.AutoWorld import World
from worlds.LauncherComponent import Component, components, launch_subprocess, Type
from .Items import TItem, get_items_by_category, item_table, item_groups
from .Locations import location_table
from .Options import Th18Options
from .Regions import create_regions
from .Rules import set_rules
from .variables.meta_data import *

def launch_client():
    from worlds.th18.Client import launch
    launch_subprocess(launch, name="GameClient")

components.append(Component(
    SHORT_NAME+" Client",
    "GameClient",
    func=launch_client,
    component_type=Type.CLIENT
))

class TWorld(World):
    game = DISPLAY_NAME