from BaseClasses import Entrance, Region

def create_and_connect_regions(world) -> None:
    create_regions(world)
    connect_regions(world)

def create_regions(world) -> None:
    regions_list = []
    ex_region = Region("Menu", world.player, world.multiworld)
    made_up_region_two = Region("Second", world.player, world.multiworld)
    regions_list.append(ex_region)
    regions_list.append(made_up_region_two)

    world.multiworld.regions += regions_list

def connect_regions(world) -> None:
    ex_region = world.get_region("Menu")
    made_up_region_two = world.get_region("Second")

    ex_region.connect(made_up_region_two, "EntranceMadeUp")