from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld
from .variables.meta_data import DISPLAY_NAME

class TouhouUMWebWorld(WebWorld):
    game = DISPLAY_NAME
    #???
    theme = "partyTime"

    setup_en = [Tutorial(
        "Multiworld Setup Guide",
    )]