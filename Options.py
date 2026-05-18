from dataclasses import dataclass
from Options import *

class DifficultyChecks(Toggle):
    """
    Separate checks by difficulty
    """
    display_name = "Difficulty Checks"

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
    split_by_difficulty: DifficultyChecks

