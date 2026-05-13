from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification

from .variables.meta_data import DISPLAY_NAME

CATEGORY_ITEM = ""
CATEGORY_FILLER = ""
CATEGORY_STAGE = ""
CATEGORY_TRAP = ""
CATEGORY_CARD = ""
CATEGORY_DIFFICULTY = ""

class TouhouUMItem(Item):
    game: str = DISPLAY_NAME