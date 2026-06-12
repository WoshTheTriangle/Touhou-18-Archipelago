from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule
from .Items import *
from .variables.card_constants import *
from .UMOptions import *

from rule_builder.rules import Has, HasAll, HasAny, HasFromListUnique, Rule, True_, False_
from rule_builder.options import OptionFilter


def set_all_rules(world) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world) -> None:
    character_rule = None
    stage_rule = None
    global_unlock_rule = None
    per_character_unlock_rule = None

    global_stage_unlock = True_() if world.options.stage_unlock.value == 0 else False_()
    per_character_unlock = True_() if world.options.stage_unlock.value == 2 else False_()

    difficulty_toggle = world.options.difficulty_check
    exclude_lunatic = world.options.exclude_lunatic
    extra_stage = world.options.extra_stage.value

    lower_difficulty_index = 0

    entrance_name = None

    # Non-difficulty check stages
    if not difficulty_toggle:
        for character in CHARACTER_NAMES:
            for stage in range(1, 7):
                if stage != 1:
                    global_unlock_rule = Has("Next Stage", count = stage - 1) & global_stage_unlock
                    per_character_unlock_rule = Has(f"[{character}] Next Stage", count = stage - 1) & per_character_unlock
                else:
                    global_unlock_rule = True_()
                    per_character_unlock_rule = True_()

                stage_rule = Has(character) & (global_unlock_rule | per_character_unlock_rule)

                #print(global_unlock_rule)
                entrance_name = world.get_entrance(f"[{character}] Enter Stage {stage}")
                world.set_rule(entrance_name, stage_rule)

    if difficulty_toggle:
        for character in CHARACTER_NAMES:
            lower_difficulty_index = 0
            for difficulty in reversed(DIFFICULTY_NAMES):
                if exclude_lunatic and difficulty == "Lunatic": 
                    lower_difficulty_index += 1
                    continue
                for stage in range(1, 7):

                    # Accessing Each Stage. This is for the Stage Clear Location Checks
                    if lower_difficulty_index == 0:
                        entrance_name = world.get_entrance(f"[{character}] Enter Stage {stage}")
                        
                        global_unlock_rule = Has("Next Stage", count = stage - 1) & global_stage_unlock
                        per_character_unlock_rule = Has(f"[{character}] Next Stage", count = stage - 1) & per_character_unlock

                        stage_rule = Has(character) & (global_unlock_rule | per_character_unlock_rule)
                        
                        world.set_rule(entrance_name, stage_rule)

                    # The rest is for specific difficulties to include Stage Difficulty-based Location Checks
                    if stage != 1:
                        global_unlock_rule = Has("Next Stage", count = stage - 1) & global_stage_unlock
                        per_character_unlock_rule = Has(f"[{character}] Next Stage", count = stage - 1) & per_character_unlock
                    else:
                        global_unlock_rule = True_()
                        per_character_unlock_rule = True_()
                    
                    if lower_difficulty_index != 0:
                        lower_difficulty_rule = Has("Lower Difficulty", count = lower_difficulty_index)
                    else:
                        lower_difficulty_rule = True_()

                    stage_rule = Has(character) & lower_difficulty_rule & (global_unlock_rule | per_character_unlock_rule)

                    entrance_name = world.get_entrance(f"[{difficulty}][{character}] Enter Stage {stage}")

                    world.set_rule(entrance_name, stage_rule)
                lower_difficulty_index += 1

    entrance_name = world.get_entrance("Alternate Ending")
    world.set_rule(entrance_name, Has(BLANK_CARD_NAME))

    # Extra Stage 
    if extra_stage != EXTRA_NOT_INCLUDED:
        if extra_stage == EXTRA_APART:
            for character in CHARACTER_NAMES:
                global_unlock_rule = Has("Extra Stage") & global_stage_unlock
                per_character_unlock_rule = Has(f"[{character}] Extra Stage") & per_character_unlock
                stage_rule = Has(character) & Has(MAGATAMA_CARD_NAME) & (global_unlock_rule | per_character_unlock_rule)

                entrance_name = world.get_entrance(f"[{character}] Enter Stage Extra")
                world.set_rule(entrance_name, stage_rule)
        elif extra_stage == EXTRA_LINEAR:
            for character in CHARACTER_NAMES:
                global_unlock_rule = Has("Next Stage", count = 6) & global_stage_unlock
                per_character_unlock_rule = Has(f"[{character}] Next Stage", count = 6) & per_character_unlock
                stage_rule = Has(character) & Has(MAGATAMA_CARD_NAME) & (global_unlock_rule | per_character_unlock_rule)

                entrance_name = world.get_entrance(f"[{character}] Enter Stage Extra")

                world.set_rule(entrance_name, stage_rule)


def set_all_location_rules(world) -> None:
    # Setting the rules for the Sky-Blue Magatama, Blank Card, and post-stage 6 character cards
    magatama_requirement = world.options.magatama_req.value
    blank_card_requirement = world.options.blank_card_req.value
    
    card_list = [item_id_to_name_table[card_id] for card_id in CARD_ITEMS_LIST]

    blank_card_location = world.get_location(f"Unlocked {BLANK_CARD_NAME}")
    world.set_rule(blank_card_location, HasFromListUnique(*card_list, count = blank_card_requirement))

    magatama_card_location = world.get_location(f"Unlocked {MAGATAMA_CARD_NAME}")
    world.set_rule(magatama_card_location, HasFromListUnique(*card_list, count = magatama_requirement))

    for character in CHARACTERS:
        player_card_location = world.get_location(f"Purchased {POST_VICTORY_CARDS[character]}")
        world.set_rule(player_card_location, Has(f"[{CHARACTER_NAMES[character]}] Defeated Chimata Ending") 
                                            | Has(f"[{CHARACTER_NAMES[character]}][Blank Card] Defeated Chimata Ending"))

    # Victory Conditions are per character.
    for character in CHARACTER_NAMES:
        location_name = world.get_location(f"[{character}] Defeated Chimata Ending")
        world.set_rule(location_name, Has(character))
        location_name = world.get_location(f"[{character}][Blank Card] Defeated Chimata Ending")
        world.set_rule(location_name, Has(character))

        if world.options.extra_stage != EXTRA_NOT_INCLUDED:
            location_name = world.get_location(f"[{character}] Defeated Momoyo")
            world.set_rule(location_name, Has(character))


def set_completion_condition(world) -> None:
    # Frogs go mlem mlem, snakes go psbpspsbsb
    # Thanks for comign folks!
    goal_condition = world.options.goal.value
    character_count = world.options.ending_req.value
    card_goal_count = world.options.card_req.value

    chimata_rule = None
    chimata_alt_rule = None
    momoyo_rule = None
    item_rule = None
    goal_rule = None

    chimata_list = [item_id_to_name_table[card_id] for card_id in GOAL_CHIMATA_ITEMS]
    chimata_alt_list = [item_id_to_name_table[card_id] for card_id in GOAL_CHIMATA_BLANK_ITEMS]
    momoyo_list = [item_id_to_name_table[card_id] for card_id in GOAL_MOMOYO_ITEMS]
    card_list = [item_id_to_name_table[card_id] for card_id in CARD_ITEMS_LIST]

    # Conflicts regarding extra not being included and choosing momoyo as a goal
    # is fixed in generate_early() in __init__

    if goal_condition == GOAL_CHIMATA or goal_condition == GOAL_ALL:
        chimata_rule = HasFromListUnique(*chimata_list, count = character_count)
        goal_rule = chimata_rule

    if goal_condition == GOAL_CHIMATA_BLANK or goal_condition == GOAL_ALL:
        chimata_alt_rule = HasFromListUnique(*chimata_alt_list, count = character_count)
        goal_rule = chimata_alt_rule
    
    if goal_condition == GOAL_MOMOYO or goal_condition == GOAL_ALL:
        momoyo_rule = HasFromListUnique(*momoyo_list, count = character_count)
        goal_rule = momoyo_rule

    if goal_condition == GOAL_ITEMS or goal_condition == GOAL_ALL:    
        item_rule = HasFromListUnique(*card_list, count = card_goal_count)
        goal_rule = item_rule

    if goal_condition == GOAL_ALL:
        goal_rule = chimata_rule & chimata_alt_rule & item_rule
        if world.options.extra_stage != EXTRA_NOT_INCLUDED:
            goal_rule = goal_rule & momoyo_rule

    world.set_completion_rule(goal_rule) 