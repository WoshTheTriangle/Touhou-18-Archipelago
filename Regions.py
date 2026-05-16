from BaseClasses import Entrance, Region

def create_regions(world) -> None:
    regions_list = []
    ex_region = Region("Test", world.player, world.multiworld)
    regions_list.append(ex_region)

    world.multiworld.regions += regions_list
