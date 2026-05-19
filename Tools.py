import pymem
import pymem.exception
import math

from .Locations import location_table
from .variables.stage_constants import *
from .variables.card_constants import *
from .GameHandler import *

# Our invaluable tool to get addresses from nested pointers.    
# Goes in the order of:
# Dereference -> Offset -> Deference -> ... -> Offset
def getPointerAddress(pm, base, offsets) -> int:
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset

    return pm.read_uint(address) + offsets[-1]

# This function maps location ids to the specific mapping used by
# gameHandler's bossesBeaten 4D list. Serves as a tool to make checking
# stage related locations much easier.
def getStageLocationMapping(split_by_difficulty: bool):

    mapping = {}
    for location_name, id in location_table.items():
        character_id = -1
        difficulty_id = -1 # Will be unchanged if split_by_difficulty is true.
        stage_id = -1
        counter_id = 0

        # Start off by checking if the location name is a valid stage location.
        valid_location = False
        if "Stage" in location_name:
            valid_location = True

        # You beat the game.
        if "Completed" in location_name:
            valid_location = True

        # Extra stage checks
        for check in EXTRA_CHECKS:
            if location_name.endswith(check):
                valid_location = True
                break

        # Searching for difficulty locations.
        if not valid_location:
            found_one = False
            for difficulty_name in DIFFICULTY_NAMES:
                if difficulty_name in location_name:
                    found_one = True
                    if split_by_difficulty:
                        valid_location = True

            if found_one and not split_by_difficulty:
                break

        # Character ID
        for character in CHARACTER_NAMES:
            if character in location_name:
                valid_location = True
                character_id = CHARACTER_NAMES_TO_ID[character]
                break

        # Leave if it is a card-related location.
        if not valid_location:
            continue

        # Difficulty
        if split_by_difficulty:
            difficulty_counter = -1
            for difficulty_name in DIFFICULTY_NAMES:
                difficulty_counter += 1
                if difficulty_name in location_name:
                    difficulty_id = difficulty_counter
                    break

        # If it is a stage clear, it is checked upon beating the stage boss.
        if "Stage" in location_name:
            counter_id = 1
            level_id = location_name.split(" ")[-2]
            if level_id == "Extra":
                stage_id = 6
            else:
                stage_id = int(level_id) - 1
        elif "Completed" in location_name:
            stage_id = 5
            counter_id = 1
        # Get both the stage number and counter number.
        else: 
            level_id = -1
            for stage in STAGE_CHECKS:
                level_id += 1
                temp_counter = -1
                for check in stage:
                    temp_counter += 1
                    if check in location_name:
                        stage_id = level_id
                        counter_id = temp_counter
                        break

                if stage_id >= 0:
                    break

        mapping[id] = [character_id, stage_id, counter_id, difficulty_id]
    return mapping


def shop_card_id_to_card_id(handler, shop_card_list: list):
    base_address = handler.gameController.pm.base_address
    return_list = []
    for shop_card in shop_card_list:
        return_list.append(SHOP_CARD_ID_TO_CARD_ID[shop_card - base_address])

    return return_list
