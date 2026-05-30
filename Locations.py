from typing import Dict

from BaseClasses import ItemClassification, Location

from .variables.card_constants import *
from .variables.meta_data import *
from .variables.stage_constants import *

class TouhouUMLocation(Location):
    game: str = SHORT_NAME

# Just testing one region for now.
def create_all_locations(world) -> None:
    region_ofchoice = world.get_region("Menu")
    region_ofchoice.add_locations(location_table, TouhouUMLocation)

# Grab a subset of location_table based off names given.
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    location_dict = {}
    for name in location_names:
        location_dict[name] = location_table[name]
    return location_dict

# Helper function to make stage location names easier to get.
def write_boss_location_name(character: str, check: str, difficulty: str = None) -> str:
    if(difficulty != None):
        return f"[{difficulty}][{character}] - {check}"
    return f"[{character}] - {check}"

location_groups : Dict[str, set[str]] = {}


location_offset = 1
location_table = {} # Name to ID 
location_id_to_name = {} # ID to Name
location_card_id_to_name_id = {}

# Boss Locations
for character in CHARACTER_NAMES:
    stage_num = 0
    for stage in STAGE_CHECKS:
        stage_num += 1
        for check in stage:
            location = write_boss_location_name(character, check)
            location_table[location] = location_offset
            location_id_to_name[location_offset] = location

            location_offset += 1
        
        # Stage Clear Locations
        
        stage_num = "Extra" if stage_num == 7 else stage_num
        location = f"[{character}] Stage {stage_num} Clear"
        location_table[location] = location_offset
        location_id_to_name[location_offset] = location

        location_offset += 1

for difficulty in DIFFICULTY_NAMES:
    for character in CHARACTER_NAMES:
        stage_num = 0
        for stage in STAGE_CHECKS:
            stage_num += 1
            if stage_num == 7:
                continue
            for check in stage:
                location = write_boss_location_name(character, check, difficulty)
                location_table[location] = location_offset
                location_id_to_name[location_offset] = location
                location_offset += 1

# Card Purchase Locations
for card in ABILITY_CARD_LIST:
    card_name = CARD_ID_TO_NAME[card]
    location = f"Purchased {card_name}"
    location_table[location] = location_offset
    location_id_to_name[location_offset] = location
    location_offset += 1

# Blank Card
location = f"Unlocked {BLANK_CARD_NAME}"
location_table[location] = location_offset
location_id_to_name[location_offset] = location
location_offset += 1

# Sky-Blue Magatama
location = f"Unlocked {MAGATAMA_CARD_NAME}"
location_table[location] = location_offset
location_id_to_name[location_offset] = location
location_offset += 1

# Endings Locations
for character in CHARACTER_NAMES:
    location = f"[{character}] Defeated Chimata Ending"
    location_table[location] = location_offset
    location_id_to_name[location_offset] = location
    location_offset += 1

for character in CHARACTER_NAMES:
    location = f"[{character}][Blank Card] Defeated Chimata Ending"
    location_table[location] = location_offset
    location_id_to_name[location_offset] = location
    location_offset += 1

for character in CHARACTER_NAMES:
    location = f"[{character}] Defeated Momoyo"
    location_table[location] = location_offset
    location_id_to_name[location_offset] = location
    location_offset += 1
