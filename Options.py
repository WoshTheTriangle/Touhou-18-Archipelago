from dataclasses import dataclass
from Options import *

class TrapChance(Range):
    """
    Percent chance that any filler item gets replaced by a trap item.
    """

    display_name = "Trap Chance"
    range_start = 0
    range_end = 100
    default = 10

@dataclass
class Th18Options(PerGameCommonOptions):
    trap_chance: TrapChance
    start_inventory_from_pool: StartInventoryPool

