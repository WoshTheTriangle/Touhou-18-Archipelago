from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from .variables.meta_data import DISPLAY_NAME

class TouhouUMWebWorld(WebWorld):
    game = DISPLAY_NAME
    #TODO   stuff
    theme = "partyTime"

    setup_en = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Touhou 18 for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["WoshTheTriangle"],
    )]