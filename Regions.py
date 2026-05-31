from BaseClasses import Entrance, Region
from .Locations import *
from .variables.stage_constants import *
from .variables.card_constants import *

def create_and_connect_regions(world) -> None:
    create_regions(world)
    connect_regions(world)
    #create_events(world)

def create_events(world) -> None:
    print("h")

def create_regions(world) -> None:
    exclude_lunatic = world.options.exclude_lunatic
    extra_stage_acquire = world.options.extra_stage
    split_by_difficulty = world.options.difficulty_check

    regions_list = generate_regions(world, exclude_lunatic, extra_stage_acquire, split_by_difficulty)

    world.multiworld.regions += regions_list

# Creates all regions with their respective locations added on.
def generate_regions(world, exclude_lunatic, extra_stage_acquire, split_by_difficulty) -> list[Region]:
    region_list = []

    victory_location = None
    victory_location_name = None
    blank_and_magatama_location = None

    init_region = Region("Menu", world.player, world.multiworld)
    region_list.append(init_region)

    card_names = [name for name in NAME_TO_CARD_ID if name not in STAGE_EXCLUSIVE_SHOP_CARDS]
    card_location_names = [f"Purchased {card_name}" for card_name in card_names]

    card_locations = get_location_names_with_ids(card_location_names)

    # Card Shop Regions + Locations
    for stage in range(1, 6):
        region_shop = Region(f"Stage {stage} Shop", world.player, world.multiworld)
        if stage == 1:
            region_shop.add_locations(card_locations, TouhouUMLocation)

        if stage == 5:
            region_shop.add_locations(get_location_names_with_ids([f"Purchased {STAGE_EXCLUSIVE_SHOP_CARDS[4]}"])
                                     | get_location_names_with_ids([f"Purchased {STAGE_EXCLUSIVE_SHOP_CARDS[5]}"]), TouhouUMLocation)
        else:
            region_shop.add_locations(get_location_names_with_ids([f"Purchased {STAGE_EXCLUSIVE_SHOP_CARDS[stage - 1]}"]), TouhouUMLocation)

        region_list.append(region_shop)

    stage_region = None
    # Stage Regions
    if not split_by_difficulty:
        for stage in range(1, 7):
            for character in CHARACTER_NAMES:
                stage_region = Region(f"[{character}] Stage {stage}", world.player, world.multiworld)

                stage_region.add_locations(get_location_names_with_ids([f"[{character}] - {check}" 
                                                                        for check in STAGE_CHECKS[stage - 1]]), TouhouUMLocation)
                stage_region.add_locations(get_location_names_with_ids([f"[{character}] Stage {stage} Clear"]), TouhouUMLocation)
                    
                region_list.append(stage_region)
    elif split_by_difficulty:
        for stage in range(1, 7):
            for character in CHARACTER_NAMES:

                stage_region = Region(f"[{character}] Stage {stage}", world.player, world.multiworld)
                stage_region.add_locations(get_location_names_with_ids([f"[{character}] Stage {stage} Clear"]), TouhouUMLocation)

                region_list.append(stage_region)

                for difficulty in DIFFICULTY_NAMES:
                    if exclude_lunatic and difficulty == "Lunatic":
                        continue

                    stage_region = Region(f"[{difficulty}][{character}] Stage {stage}", world.player, world.multiworld)
                    stage_region.add_locations(get_location_names_with_ids([f"[{difficulty}][{character}] - {check}" 
                                                                            for check in STAGE_CHECKS[stage - 1]]), TouhouUMLocation)
                    region_list.append(stage_region)

    # We have extra stages enabled.
    if extra_stage_acquire != EXTRA_NOT_INCLUDED:
        for character in CHARACTER_NAMES:
            stage_region = Region(f"[{character}] Stage Extra", world.player, world.multiworld)

            stage_region.add_locations(get_location_names_with_ids([f"[{character}] - {check}"
                                        for check in STAGE_CHECKS[6]]), TouhouUMLocation)
            stage_region.add_locations(get_location_names_with_ids([f"[{character}] Stage Extra Clear"]), TouhouUMLocation)

            # Victory location (fixed items) for defeating Momoyo
            victory_location_name = f"[{character}] Defeated Momoyo"
            victory_location = TouhouUMLocation(world.player, victory_location_name, location_table[victory_location_name], stage_region)
            victory_location.place_locked_item(world.create_item(victory_location_name))
            stage_region.locations.append(victory_location)

            region_list.append(stage_region)

        stage_region = Region("Extra Stage Clear", world.player, world.multiworld)
        stage_region.add_locations(get_location_names_with_ids([f"Purchased {MOMOYO_CARD_NAME}"]), TouhouUMLocation)
        region_list.append(stage_region)

    # Beating the game.
    stage_region = Region("Beat The Game", world.player, world.multiworld)

    # Victory locations (these are fixed)
    
    for character in CHARACTER_NAMES:
        victory_location_name = f"[{character}] Defeated Chimata Ending"
        victory_location = TouhouUMLocation(world.player, victory_location_name, location_table[victory_location_name], stage_region)
        victory_location.place_locked_item(world.create_item(victory_location_name))

        stage_region.locations.append(victory_location)
    region_list.append(stage_region)

    stage_region = Region("Beat The Game [Alternate]", world.player, world.multiworld)

    for character in CHARACTER_NAMES:
        victory_location_name = f"[{character}][Blank Card] Defeated Chimata Ending"
        victory_location = TouhouUMLocation(world.player, victory_location_name, location_table[victory_location_name], stage_region)
        victory_location.place_locked_item(world.create_item(victory_location_name))

        stage_region.locations.append(victory_location)
    region_list.append(stage_region)

    stage_region = init_region
    # Placing Blank Card and Sky-Blue Magatama in the locations.
    blank_and_magatama_location = TouhouUMLocation(world.player, f"Unlocked {BLANK_CARD_NAME}", location_table[f"Unlocked {BLANK_CARD_NAME}"], init_region)
    blank_and_magatama_location.place_locked_item(world.create_item(BLANK_CARD_NAME))
    stage_region.locations.append(blank_and_magatama_location)


    blank_and_magatama_location = TouhouUMLocation(world.player, f"Unlocked {MAGATAMA_CARD_NAME}", location_table[f"Unlocked {MAGATAMA_CARD_NAME}"], init_region)
    blank_and_magatama_location.place_locked_item(world.create_item(MAGATAMA_CARD_NAME))
    stage_region.locations.append(blank_and_magatama_location)

    return region_list

# Connect all regions together. Creates Entrances.
def connect_regions(world) -> None:
    exclude_lunatic = world.options.exclude_lunatic
    extra_stage_acquire = world.options.extra_stage
    split_by_difficulty = world.options.difficulty_check

    menu_region = world.get_region("Menu")
    # Connecting character regions
    starting_region = menu_region
    connecting_region = None

    # Stage and shop connections. Not split by difficulty.
    
    for character in CHARACTER_NAMES:
        starting_region = menu_region
        for stage in range(1, 7):

            # Connect previous stage shop (or menu) to current stage.
            connecting_region = world.get_region(f"[{character}] Stage {stage}")
            starting_region.connect(connecting_region, f"[{character}] Enter Stage {stage}")

            # Connect current stage to current shop unless on stage 6.
            if stage == 6:

                starting_region = connecting_region
                connecting_region = world.get_region("Beat The Game")

                starting_region.connect(connecting_region, f"[{character}] Completed the Game")
                continue

            starting_region = connecting_region
            connecting_region = world.get_region(f"Stage {stage} Shop")

            starting_region.connect(connecting_region, f"[{character}] Enter Stage {stage} Shop")

            starting_region = connecting_region

    # stage_region = Region(f"[{character}] Stage {stage}", world.player, world.multiworld)
    # stage_region.add_locations(get_location_names_with_ids([f"[{character}] Stage {stage} Clear"]), TouhouUMLocation)

    # Difficulty connections.
    if split_by_difficulty:
        for character in CHARACTER_NAMES:
            for difficulty in DIFFICULTY_NAMES:
                if exclude_lunatic and difficulty == "Lunatic":
                    continue

                starting_region = menu_region
                for stage in range(1, 7):

                    # Connect previous stage shop (or menu) to current stage.
                    connecting_region = world.get_region(f"[{difficulty}][{character}] Stage {stage}")
                    starting_region.connect(connecting_region, f"[{difficulty}][{character}] Enter Stage {stage}")

                    # Connect current stage to current shop (or game completion).
                    if stage == 6:
                        starting_region = connecting_region
                        connecting_region = world.get_region("Beat The Game")
                        starting_region.connect(connecting_region, f"[{difficulty}][{character}]Completed the Game")
                        continue

                    starting_region = connecting_region
                    connecting_region = world.get_region(f"Stage {stage} Shop")

                    starting_region.connect(connecting_region, f"[{difficulty}][{character}]Enter Stage {stage} Shop")

                    starting_region = connecting_region

    starting_region = world.get_region("Beat The Game")
    connecting_region = world.get_region("Beat The Game [Alternate]")
    starting_region.connect(connecting_region, "Alternate Ending")

    # Extra Stage Connections.
    for character in CHARACTER_NAMES:
        starting_region = menu_region
        if extra_stage_acquire != EXTRA_NOT_INCLUDED:
            if extra_stage_acquire == EXTRA_APART: # Extra connected to main menu
                connecting_region = world.get_region(f"[{character}] Stage Extra")
                starting_region.connect(connecting_region, f"[{character}] Enter Stage Extra")
            elif extra_stage_acquire == EXTRA_LINEAR: # Extra connected to beating stage 6
                starting_region = world.get_region("Beat The Game")
                connecting_region = world.get_region(f"[{character}] Stage Extra")
                starting_region.connect(connecting_region, f"[{character}] Enter Stage Extra")

            starting_region = world.get_region(f"[{character}] Stage Extra")
            connecting_region = world.get_region("Extra Stage Clear")
            starting_region.connect(connecting_region, f"[{character}] Beat Extra Stage")
