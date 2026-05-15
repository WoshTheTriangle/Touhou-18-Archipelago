from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification

from .variables.meta_data import DISPLAY_NAME
from .variables.card_constants import *

CATEGORY_ITEM = "Useful Items"
CATEGORY_FILLER = "Filler"
CATEGORY_STAGE = "Stage Progression"
CATEGORY_CHARACTER = "Character Unlock"
CATEGORY_TRAP = "Trap"
CATEGORY_CARD = "Ability Cards"

class TouhouUMItem(Item):
    game: str = DISPLAY_NAME

class TouhouUMItemData(NamedTuple):
    category: str
    code: Optional[int] = None
    classification: ItemClassification = ItemClassification.filler
    max_quantity: int = 1
    weight: int = 1

def get_random_filler_item_name(world):
    print("to be made")

def create_items(world):
    print("to be made")

item_table: Dict[str, TouhouUMItemData] = {
    # Useful for Stage Completion
    "+1 Max Life" : TouhouUMItemData(CATEGORY_STAGE, 1, ItemClassification.progression, 8),
    "+1 Max Bomb" : TouhouUMItemData(CATEGORY_STAGE, 2, ItemClassification.progression, 8),
    "+1 Continue" : TouhouUMItemData(CATEGORY_ITEM, 3, ItemClassification.useful, 5),
    "Lower Difficulty" : TouhouUMItem(CATEGORY_ITEM, 4, ItemClassification.progression, 3), #maybe useful later idk
    "Extra Starting Card Slot" : TouhouUMItem(CATEGORY_ITEM, 5, ItemClassification.useful, 2),
    "+50 Funds" : TouhouUMItemData(CATEGORY_ITEM, 6, ItemClassification.useful, 3),
    "+75 Funds" : TouhouUMItemData(CATEGORY_ITEM, 7, ItemClassification.useful, 3),
    "+100 Funds" : TouhouUMItemData(CATEGORY_ITEM, 8, ItemClassification.useful, 3),
    "+50 Power" : TouhouUMItemData(CATEGORY_ITEM, 9, ItemClassification.useful, 3),
    "+75 Power" : TouhouUMItemData(CATEGORY_ITEM, 10, ItemClassification.useful, 3),
    "+100 Power" : TouhouUMItemData(CATEGORY_ITEM, 11, ItemClassification.useful, 3),

    # Characters
    "Reimu" : TouhouUMItemData(CATEGORY_CHARACTER, 100, ItemClassification.progression),
    "Marisa" : TouhouUMItemData(CATEGORY_CHARACTER, 101, ItemClassification.progression),
    "Sakuya" : TouhouUMItemData(CATEGORY_CHARACTER, 102, ItemClassification.progression),
    "Sanae" : TouhouUMItemData(CATEGORY_CHARACTER, 103, ItemClassification.progression),
    
    #Stages
    "Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 200, ItemClassification.progression, 7),
    "[Reimu] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 201, ItemClassification.progression, 7),
    "[Marisa] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 202, ItemClassification.progression, 7),
    "[Sakuya] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 203, ItemClassification.progression, 7),
    "[Sanae] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 204, ItemClassification.progression, 7),
    "Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),
    "[Reimu] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),
    "[Marisa] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),
    "[Sakuya] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),
    "[Sanae] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),

    #Ability Cards
    LIFE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 300, ItemClassification.progression),
    SPELL_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 301, ItemClassification.progression),
    LIFE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 302, ItemClassification.progression),
    NAZRIN_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 303, ItemClassification.progression),
    RINGO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 304, ItemClassification.progression),
    MOKOU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 305, ItemClassification.progression),
    MIKE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 306, ItemClassification.progression),
    TAKANE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 307, ItemClassification.progression),
    SANNYO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 308, ItemClassification.progression),
    NARUMI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 309, ItemClassification.progression),
    PATCHOULI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 310, ItemClassification.progression),
    YOUMU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 311, ItemClassification.progression),
    REIMU1_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 312, ItemClassification.progression),
    ALICE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 313, ItemClassification.progression),
    CIRNO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 314, ItemClassification.progression),
    REIMU2_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 315, ItemClassification.progression),
    MARISA1_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 316, ItemClassification.progression),
    MARISA2_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 317, ItemClassification.progression),
    SAKUYA1_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 318, ItemClassification.progression),
    SAKUYA2_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 319, ItemClassification.progression),
    SANAE1_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 320, ItemClassification.progression),
    SANAE2_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 321, ItemClassification.progression),
    OKINA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 322, ItemClassification.progression),
    NUE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 323, ItemClassification.progression),
    TEWI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 324, ItemClassification.progression),
    EIRIN_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 325, ItemClassification.progression),
    NITORI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 326, ItemClassification.progression),
    SAKI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 327, ItemClassification.progression),
    KOISHI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 328, ItemClassification.progression),
    KANAKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 329, ItemClassification.progression),
    BYAKUREN_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 330, ItemClassification.progression),
    SUWAKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 331, ItemClassification.progression),
    AYA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 332, ItemClassification.progression),
    KEIKI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 333, ItemClassification.progression),
    KAGUYA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 334, ItemClassification.progression),
    MAMIZOU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 335, ItemClassification.progression),
    YUYUKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 336, ItemClassification.progression),
    YACHIE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 337, ItemClassification.progression),
    SHIKIEIKI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 338, ItemClassification.progression),
    SHINMYOUMARU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 339, ItemClassification.progression),
    YUKARI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 340, ItemClassification.progression),
    TENSHI_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 341, ItemClassification.progression),
    CLOWNPIECE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 342, ItemClassification.progression),
    RAIKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 343, ItemClassification.progression),
    MIKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 344, ItemClassification.progression),
    REMILIA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 345, ItemClassification.progression),
    UTSUHO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 346, ItemClassification.progression),
    LILYWHITE_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 347, ItemClassification.progression),
    SUMIREKO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 348, ItemClassification.progression),
    MISUMARU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 349, ItemClassification.progression),
    TSUKASA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 350, ItemClassification.progression),
    MEGUMU_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 351, ItemClassification.progression),
    MOMOYO_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 352, ItemClassification.progression),
    MAGATAMA_CARD_NAME : TouhouUMItemData(CATEGORY_CARD, 353, ItemClassification.progression),

    #Filler
    "+10 Funds" : TouhouUMItemData(CATEGORY_FILLER, 400, ItemClassification.filler),
    "+25 Funds" : TouhouUMItemData(CATEGORY_FILLER, 401, ItemClassification.filler),
    "+1 Power" : TouhouUMItemData(CATEGORY_FILLER, 402, ItemClassification.filler),
    "+10 Power" : TouhouUMItemData(CATEGORY_FILLER, 403, ItemClassification.filler),
    "+1 Life Fragment" : TouhouUMItemData(CATEGORY_FILLER, 404, ItemClassification.filler),
    "+1 Bomb Fragment" : TouhouUMItemData(CATEGORY_FILLER, 405, ItemClassification.filler),

    # Traps
    "Frozen Movement" : TouhouUMItemData(CATEGORY_TRAP, 500, ItemClassification.trap),
    "Increased Speed" : TouhouUMItemData(CATEGORY_TRAP, 501, ItemClassification.trap),
    "Inverse Movement" : TouhouUMItemData(CATEGORY_TRAP, 502, ItemClassification.trap),
    "-10 Funds" : TouhouUMItemData(CATEGORY_TRAP, 503, ItemClassification.trap),
    "-50 Funds" : TouhouUMItemData(CATEGORY_TRAP, 504, ItemClassification.trap),
    "-100 Funds" : TouhouUMItemData(CATEGORY_TRAP, 505, ItemClassification.trap),
    "-25 Power" : TouhouUMItemData(CATEGORY_TRAP, 506, ItemClassification.trap),
    "-50 Power" : TouhouUMItemData(CATEGORY_TRAP, 507, ItemClassification.trap),
    "50% Damage" : TouhouUMItemData(CATEGORY_TRAP, 508, ItemClassification.trap),
    "Death" : TouhouUMItemData(CATEGORY_TRAP, 509, ItemClassification.trap),
}