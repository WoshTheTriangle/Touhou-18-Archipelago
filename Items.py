from typing import Dict, NamedTuple, Optional

import time

from BaseClasses import Item, ItemClassification

from .variables.meta_data import DISPLAY_NAME
from .variables.card_constants import *
from .variables.stage_constants import *

CATEGORY_ITEM = "Useful Items"
CATEGORY_FILLER = "Filler"
CATEGORY_STAGE = "Stage Progression"
CATEGORY_CHARACTER = "Character Unlock"
CATEGORY_TRAP = "Trap"
CATEGORY_CARD = "Ability Cards"
CATEGORY_VICTORY = "Victory"

class TouhouUMItem(Item):
    game: str = DISPLAY_NAME

class TouhouUMItemData(NamedTuple):
    category: str
    code: Optional[int] = None
    classification: ItemClassification = ItemClassification.filler
    max_quantity: int = 1
    weight: int = 1

# May be edited to exclude certain traps.
def get_random_trap(world) -> str:
    trap_list = []
    for name in trap_table.keys():
        trap_list.append(name)
    return world.random.choice(trap_list).__str__()

# May be edited to exclude certain fillers.
def get_random_filler(world) -> str:
    filler_list = []
    for name in filler_table.keys():
        filler_list.append(name)
    return world.random.choice(filler_list).__str__()


def get_random_filler_item_name(world) -> str:
    if world.random.randint(0, 99) < world.options.trap_chance:
        return get_random_trap(world)
    return get_random_filler(world)

def create_item_with_correct_classification(world, name: str) -> TouhouUMItem:
    item = item_table[name]
    return TouhouUMItem(name, item.classification, item.code, world.player)


def create_all_items(world) -> None:
    item_pool: List[Item] = []
    for item, data in item_table.items():

        # Less Difficulty Options
        if data.code == 4 and world.options.exclude_lunatic:
            #print("EXCLUDE LUNATIC")
            for i in range(3):
                item_pool.append(world.create_item(item))
            continue

        # Amount of progressive lives if there is a max limit without items increasing the cap.
        if data.code == 1 and not world.options.max_life_item:
            #print("PROGRESSIVE LIVES")
            for i in range(world.options.init_max_lives):
                item_pool.append(world.create_item(item))
            continue
        
        # Amount of progressive bombs if there is a max limit without items increasing the cap.
        if data.code == 2 and not world.options.max_bomb_item:
            #print("PROGRESSIVE BOMBS")
            for i in range(world.options.init_max_bombs):
                item_pool.append(world.create_item(item))
            continue

        # Adding max lives
        if data.code == 12 and world.options.max_life_item:
            #print("MAX LIVES")
            for i in range(8 - world.options.init_max_lives):
                item_pool.append(world.create_item(item))
            continue
            
        # Adding max bombs.
        if data.code == 13 and world.options.max_bomb_item:
            #print("MAX BOMBS")
            for i in range(8 - world.options.init_max_bombs):
                item_pool.append(world.create_item(item))
            continue

        # Global Character Stage Unlocks.
        if data.code == 200 and world.options.stage_unlock == STAGE_GLOBAL:
            # Extra stage is an additional linear next stage.
            if world.options.extra_stage == EXTRA_LINEAR:
                #print("EXTRA IS LINEAR")
                for i in range(data.max_quantity + 1):
                    item_pool.append(world.create_item(item))
                continue
        elif data.code == 200 and world.options.stage_unlock != STAGE_GLOBAL:
            #print("NOT GLOBAL")
            continue

        # Global Character Extra Unlock
        if data.code == 205 and (world.options.stage_unlock != STAGE_GLOBAL or world.options.extra_stage != EXTRA_APART):
            #print("EXTRA IS NOT GLOBAL AND IS LINEAR")
            continue

        # Per Character Stage Unlocks.
        if (data.code >= 201 and data.code <= 204) and world.options.stage_unlock == STAGE_PER_CHARACTER:
            # Extra stage is an additional linear next stage.
            if world.options.extra_stage == EXTRA_LINEAR:
                #print("EXTRA IS PER CHARACTER LINEAR")
                for i in range(data.max_quantity + 1):
                    item_pool.append(world.create_item(item))
                continue
        elif (data.code >= 201 and data.code <= 204) and world.options.stage_unlock != STAGE_PER_CHARACTER:
            #print("EXTRA IS GLOBAL AND ")
            continue

        # Per Character Extra Unlock
        if (data.code >= 206 and data.code <= 209) and (world.options.stage_unlock != STAGE_PER_CHARACTER or world.options.extra_stage != EXTRA_APART):
            #print("EXTRA IS GLOBAL AND LINEAR")
            continue
            
        # Magatama (and Blank Card) is not automatically in the item pool.
        if data.code == 353:
            continue

        if data.category == CATEGORY_FILLER or data.category == CATEGORY_TRAP or data.category == CATEGORY_VICTORY:
            #print("FILLER")
            continue

        # Normal item which can be treated normally.
        for i in range(data.max_quantity):
            item_pool.append(world.create_item(item))

    

    # Filling up remaining required item slots.
    item_length = len(item_pool)
    num_locations = len(world.multiworld.get_unfilled_locations(world.player))
    num_filler_needed = num_locations - item_length

    for i in range(num_filler_needed):
        filler_name = world.get_filler_item_name()
        item_pool.append(world.create_item(filler_name))

    world.multiworld.itempool += item_pool


def get_item_to_id_dict() -> Dict[str, int]:
    item_dict: Dict[str, int] = {}
    for name, data in item_table.items():
        item_dict.setdefault(name, data.code)
    return item_dict


item_table: Dict[str, TouhouUMItemData] = {
    # Useful for Stage Completion
    "+1 Starting Life" : TouhouUMItemData(CATEGORY_STAGE, 1, ItemClassification.progression, 8),
    "+1 Starting Bomb" : TouhouUMItemData(CATEGORY_STAGE, 2, ItemClassification.progression, 8),
    "+1 Continue" : TouhouUMItemData(CATEGORY_ITEM, 3, ItemClassification.useful, 5),
    "Lower Difficulty" : TouhouUMItemData(CATEGORY_ITEM, 4, ItemClassification.progression, 3), #maybe useful later idk
    "Extra Starting Card Slot" : TouhouUMItemData(CATEGORY_ITEM, 5, ItemClassification.useful, 2),
    "+50 Funds" : TouhouUMItemData(CATEGORY_ITEM, 6, ItemClassification.useful, 3),
    "+100 Funds" : TouhouUMItemData(CATEGORY_ITEM, 8, ItemClassification.useful, 3),
    "+50 Power" : TouhouUMItemData(CATEGORY_ITEM, 9, ItemClassification.useful, 3),
    "+75 Power" : TouhouUMItemData(CATEGORY_ITEM, 10, ItemClassification.useful, 3),
    "+1 Max Life" : TouhouUMItemData(CATEGORY_ITEM, 12, ItemClassification.progression, 0),
    "+1 Max Bomb" : TouhouUMItemData(CATEGORY_ITEM, 13, ItemClassification.progression, 0),

    # Characters
    "Reimu" : TouhouUMItemData(CATEGORY_CHARACTER, 100, ItemClassification.progression),
    "Marisa" : TouhouUMItemData(CATEGORY_CHARACTER, 101, ItemClassification.progression),
    "Sakuya" : TouhouUMItemData(CATEGORY_CHARACTER, 102, ItemClassification.progression),
    "Sanae" : TouhouUMItemData(CATEGORY_CHARACTER, 103, ItemClassification.progression),
    
    #Stages
    "Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 200, ItemClassification.progression, 6),
    "[Reimu] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 201, ItemClassification.progression, 6),
    "[Marisa] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 202, ItemClassification.progression, 6),
    "[Sakuya] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 203, ItemClassification.progression, 6),
    "[Sanae] Next Stage" : TouhouUMItemData(CATEGORY_STAGE, 204, ItemClassification.progression, 6),
    "Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 205, ItemClassification.progression),
    "[Reimu] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 206, ItemClassification.progression),
    "[Marisa] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 207, ItemClassification.progression),
    "[Sakuya] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 208, ItemClassification.progression),
    "[Sanae] Extra Stage" : TouhouUMItemData(CATEGORY_STAGE, 209, ItemClassification.progression),

    #Ability Cards
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

    # Victory conditions
    "[Reimu] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 600, ItemClassification.progression),
    "[Marisa] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 601, ItemClassification.progression),
    "[Sakuya] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 602, ItemClassification.progression),
    "[Sanae] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 603, ItemClassification.progression),
    "[Reimu][Blank Card] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 604, ItemClassification.progression),
    "[Marisa][Blank Card] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 605, ItemClassification.progression),
    "[Sakuya][Blank Card] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 606, ItemClassification.progression),
    "[Sanae][Blank Card] Defeated Chimata Ending" : TouhouUMItemData(CATEGORY_VICTORY, 607, ItemClassification.progression),
    "[Reimu] Defeated Momoyo" : TouhouUMItemData(CATEGORY_VICTORY, 608, ItemClassification.progression),
    "[Marisa] Defeated Momoyo" : TouhouUMItemData(CATEGORY_VICTORY, 609, ItemClassification.progression),
    "[Sakuya] Defeated Momoyo" : TouhouUMItemData(CATEGORY_VICTORY, 610, ItemClassification.progression),
    "[Sanae] Defeated Momoyo" : TouhouUMItemData(CATEGORY_VICTORY, 611, ItemClassification.progression)
}

# Subsets of item_table

filler_table: Dict[str, TouhouUMItemData] = {}
for name, data in item_table.items():
    if data.category == CATEGORY_FILLER:
        filler_table.setdefault(name, data)

trap_table: Dict[str, TouhouUMItemData] = {}
for name, data in item_table.items():
    if data.category == CATEGORY_TRAP:
        trap_table.setdefault(name, data)

ITEM_ID_TO_CARD_ID: Dict[int, int] = {
    301: BOMB_CARD,
    302: LIFE_CARD,
    303: NAZRIN_CARD,
    304: RINGO_CARD,
    305: MOKOU_CARD,
    306: MIKE_CARD,
    307: TAKANE_CARD,
    308: SANNYO_CARD,
    309: NARUMI_CARD,
    310: PATCHOULI_CARD,
    311: YOUMU_CARD,
    312: REIMU1_CARD,
    313: ALICE_CARD,
    314: CIRNO_CARD, 
    315: REIMU2_CARD, 
    316: MARISA1_CARD,
    317: MARISA2_CARD, 
    318: SAKUYA1_CARD, 
    319: SAKUYA2_CARD, 
    320: SANAE1_CARD, 
    321: SANAE2_CARD, 
    322: OKINA_CARD, 
    323: NUE_CARD, 
    324: TEWI_CARD, 
    325: EIRIN_CARD, 
    326: NITORI_CARD, 
    327: SAKI_CARD,
    328: KOISHI_CARD, 
    329: KANAKO_CARD,
    330: BYAKUREN_CARD, 
    331: SUWAKO_CARD, 
    332: AYA_CARD, 
    333: KEIKI_CARD, 
    334: KAGUYA_CARD, 
    335: MAMIZOU_CARD, 
    336: YUYUKO_CARD, 
    337: YACHIE_CARD, 
    338: SHIKIEIKI_CARD, 
    339: SHINMYOUMARU_CARD, 
    340: YUKARI_CARD, 
    341: TENSHI_CARD, 
    342: CLOWNPIECE_CARD, 
    343: RAIKO_CARD, 
    344: MIKO_CARD, 
    345: REMILIA_CARD, 
    346: UTSUHO_CARD, 
    347: LILYWHITE_CARD, 
    348: SUMIREKO_CARD, 
    349: MISUMARU_CARD, 
    350: TSUKASA_CARD, 
    351: MEGUMU_CARD, 
    352: MOMOYO_CARD, 
    353: MAGATAMA_CARD, 
}

PERMANENT_ITEMS = [1, 2, 3, 4, 5,
                   100, 101, 102, 103,
                   200, 201, 202, 203, 204, 205, 206,
                   207, 208, 209,
                   600, 601, 602, 603, 604, 605, 606,
                   607, 608, 609, 610, 611]

STAGE_ONLY_ITEMS = [6, 7, 8, 9, 10, 11,
                    400, 401, 402, 403, 404, 405,
                    500, 501, 502, 503, 504, 505, 506,
                    507, 508, 509]

DURATION_BASED_ITEMS = [500, 501, 502, 508]

GOAL_BASED_ITEMS = [600, 601, 602, 603, 604, 605, 606,
                    607, 608, 609, 610, 611]

GOAL_CHIMATA_ITEMS = [600, 601, 602, 603]
GOAL_CHIMATA_BLANK_ITEMS = [604, 605, 606, 607]
GOAL_MOMOYO_ITEMS = [608, 609, 610, 611]