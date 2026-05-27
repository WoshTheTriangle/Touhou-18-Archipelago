from BaseClasses import Entrance, Region
from .Locations import *
from .variables.stage_constants import *
from .variables.card_constants import *

def create_and_connect_regions(world) -> None:
    create_regions(world)
    connect_regions(world)

def create_regions(world) -> None:
    exclude_lunatic = world.options.exclude_lunatic
    extra_stage_acquire = world.options.extra_stage
    split_by_difficulty = world.options.difficulty_check

    regions_list = generate_regions(world, exclude_lunatic, extra_stage_acquire, split_by_difficulty)

    world.multiworld.regions += regions_list

# Creates all regions with their respective locations added on.
def generate_regions(world, exclude_lunatic, extra_stage_acquire, split_by_difficulty) -> list[Region]:
    region_list = []

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

                if stage == 6:
                    stage_region.add_locations(get_location_names_with_ids([f"Completed the game as {character}"]), TouhouUMLocation)
                    
                region_list.append(stage_region)
    else:
        for stage in range(1, 7):
            for character in CHARACTER_NAMES:

                stage_region = Region(f"[{character}] Stage {stage}", world.player, world.multiworld)
                stage_region.add_locations(get_location_names_with_ids([f"[{character}] Stage {stage} Clear"]), TouhouUMLocation)

                if stage == 6:
                    stage_region.add_locations(get_location_names_with_ids([f"Completed the game as {character}"]), TouhouUMLocation)

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

            region_list.append(stage_region)

        stage_region = Region("Extra Stage Clear", world.player, world.multiworld)
        stage_region.add_locations(get_location_names_with_ids([f"Purchased {MOMOYO_CARD_NAME}"]), TouhouUMLocation)
        region_list.append(stage_region)

    # Beating the game.
    stage_region = Region("Beat The Game", world.player, world.multiworld)
    stage_region.add_locations(get_location_names_with_ids([f"Unlocked {MAGATAMA_CARD_NAME}"]), TouhouUMLocation)
    region_list.append(stage_region)

    return region_list

def connect_regions(world) -> None:
    exclude_lunatic = world.options.exclude_lunatic
    extra_stage_acquire = world.options.extra_stage
    split_by_difficulty = world.options.difficulty_check

    menu_region = world.get_region("Menu")
    # Connecting character regions
    starting_region = menu_region
    connecting_region = None

    # Stage and shop connections.
    for character in CHARACTER_NAMES:
        starting_region = menu_region
        for stage in range(1, 7):

            # Connect previous stage shop (or menu) to current stage.
            connecting_region = world.get_region(f"[{character}] Stage {stage}")
            starting_region.connect(connecting_region, f"[{character}] Enter Stage {stage}")

            # Connect current stage to current shop.
            if stage == 6:
                starting_region = connecting_region
                connecting_region = world.get_region("Beat The Game")
                starting_region.connect(connecting_region, f"[{character}] Completed the Game")
                continue

            starting_region = connecting_region
            connecting_region = world.get_region(f"Stage {stage} Shop")

            starting_region.connect(connecting_region, f"[{character}] Enter Stage {stage} Shop")

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

    # Extra Stage Connections.
    for character in CHARACTER_NAMES:
        starting_region = menu_region
        if extra_stage_acquire != EXTRA_NOT_INCLUDED:
            if extra_stage_acquire == EXTRA_APART: # Extra connected to main menu
                connecting_region = world.get_region(f"[{character}] Stage Extra")
                starting_region.connect(connecting_region, f"[{character}] Enter Stage Extra")
            elif extra_stage_acquire == EXTRA_LINEAR: # Extra connected to beating stage 6
                starting_region = world.get_region(f"Beat The Game")
                connecting_region = world.get_region(f"[{character}] Stage Extra")
                starting_region.connect(connecting_region, f"[{character}] Enter Stage Extra")

            starting_region = world.get_region(f"[{character}] Stage Extra")
            connecting_region = world.get_region("Extra Stage Clear")
            starting_region.connect(connecting_region, f"[{character}] Beat Extra Stage")
