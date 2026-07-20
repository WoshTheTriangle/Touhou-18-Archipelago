import pymem
import pymem.exception
import math

from .Locations import location_table
from .variables.stage_constants import *
from .variables.card_constants import *

def clamp(lower, upper, value) -> int:
    return max(lower, min(value, upper))


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

        '''
        Creating Mapping
        '''

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

# Returns the mapping of archipelago location IDs to card IDs for card locations.
def getAPIDsForCards():
    mapping = {}
    for location_name, id in location_table.items():
        purchase = False
        unlock = False

        if "Purchased" in location_name:
            purchase = True
        elif "Unlocked" in location_name:
            unlock = True
        else:
            continue

        if BLANK_CARD_NAME in location_name or MAGATAMA_CARD_NAME in location_name:
            continue

        if purchase:
            name = (location_name.split("Purchased ")[1])
        elif unlock:
            name = (location_name.split("Unlocked ")[1])

        value = NAME_TO_CARD_ID.get(name)
        if value == None:
            continue
        else:
            mapping[id] = value
    return mapping

def getLocationIDsToEndingMapping():
    mapping = {}
    for location_name, id in location_table.items():
        valid_location = False
        character_id = None
        goal_id = None

        if "Defeated Chimata Ending" in location_name:
            valid_location = True

        if "Defeated Momoyo" in location_name:
            valid_location = True

        if not valid_location:
            continue

        for character in CHARACTER_NAMES:
            if character in location_name:
                character_id = CHARACTER_NAMES_TO_ID[character]
                break

        goal_id = GOAL_CHIMATA

        if "[Blank Card]" in location_name:
            goal_id = GOAL_CHIMATA_BLANK
        
        if "Momoyo" in location_name:
            goal_id = GOAL_MOMOYO

        mapping[id] = [character_id, goal_id]

    return mapping