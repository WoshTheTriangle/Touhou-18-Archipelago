from dataclasses import dataclass
import Options
from Options import *

'''
class Mode(Choice):
    """
    The mode being played on.
    Normal Mode: Regular Touhou 18 with unlocks for purchasing cards. 
                 Each stage must be unlocked in order to progress.
    Practice Mode: Unlock each stage in order to progress. 
    """
    display_name = "Game Mode"

    option_normal = 0
    option_practice = 2
    default = 0
'''

class StageUnlock(Choice):
    """
    How stages are unlocked.
    Global: No group.
    Character: Stages are unlocked per character.
    """
    display_name = "Stage Unlocks"

    option_global = 0
    option_per_character = 2
    default = 0

class GuaranteeUnpurchasedCardPerShop(Toggle):
    """
    Guarantee that every shop pool has at least one unpurchased card present.
    This card will be the rightmost one and unique to all the other cards in the pool.
    No card will be created if all cards have already been purchased or no more unique unpurchased cards can exist.
    Can be changed later.
    """
    display_name = "Guarantee Unpurchased Card Per Shop"

    default = True

class ExtraStage(Choice):
    """
    How Extra Stage should be included.
    Linear: Extra Stage is acquired as the 7th progressive stage.
    Apart: Extra Stage progressions are normal items to be unlocked.
    Not Included: Extra Stage progressions are unobtainable and no locations are locked behind Extra Stage.
                  This also removes Gluttonous Centipede from the item pool, making all card ranges have an end of 51.
    """
    display_name = "Include Extra Stage"

    option_linear = 0
    option_apart = 1
    option_not_included = 3

    default = 0

class MagatamaRequirement(Range):
    """
    Amount of cards required to gain the Sky-Blue Magatama:
    (If set to 0, it is automatically obtained and you just need Extra Stage progressions to access the Extra Stage.)
    """
    display_name = "Number of Cards Needed to Unlock Sky-Blue Magatama"

    range_start = 0
    range_end = 52

    default = 5

class BlankCardRequirement(Range):
    """
    Amount of ability cards required to get the Blank Card
    """
    display_name = "Number of Cards Needed to Unlock Blank Card"

    range_start = 0
    range_end = 52
    default = 20

class Goal(Choice):
    """
    Determine the condition as the goal.
    Defeat Chimata: Defeating Chimata Tenkyuu (Complete Stage 6).
    Defeat Momoyo: Defeating Momoyo Himemushi (Complete Extra Stage).
                   If Extra Stage is not included,  it will default to defeating Chimata.
    Chimata Blank Card Ending: Defeating Chimata Tenkyuu with the Blank Card (Complete Stage 6 with Blank Card).
    Ability Cards: Acquire a certain number of ability cards.
                   Blank Card and Sky-Blue Magatama are not counted towards this number.
    All: Combined goals of Defeat Momoyo, Chimata Blank Card Ending, and Ability Cards.
    """
    display_name = "Goal"

    option_chimata = 0
    option_momoyo = 1
    option_chimata_with_blank_card = 2
    option_ability_cards = 3
    option_all = 4
    default = 0

class EndingsRequired(Range):
    """
    If Ability Cards was not chosen:
    Amount of characters required to complete the ending conditions to achieve the goal.
    """
    display_name = "Amount of characters needed to beat goal bosses"
    range_start = 1
    range_end = 4
    default = 1

class CardsRequired(Range):
    """
    If Ability Cards or All was chosen:
    The amount of ability cards required to achieve the goal.
    """
    display_name = "Amount of ability cards required to complete the goal"
    range_start = 1
    range_end = 52
    default = 30

class DifficultyCheck(Toggle):
    """
    Toggle whether checks are separated by difficulty.
    """
    display_name = "Difficulty Check"

class CheckMultipleDifficulty(Toggle):
    """
    If Difficulty Check was enabled:
    Toggle for all difficulty checks to include the checks of lower difficulties.
    """
    display_name = "Multiple Difficulty Check"

class ExcludeLunatic(Toggle):
    """
    Exclude the Lunatic Difficulty, starting off at Hard instead.
    """
    display_name = "Exclude Lunatic"

class InitLivesLimit(Range):
    """
    Limit on the maximum amount of lives that the player can have.
    """
    display_name = "Lives Limit"

    range_start = 0
    range_end = 7
    default = 7

class MaxLifeItem(Toggle):
    """
    Allow the previous maximum limit on lives to be able to be increased via items.
    Adds new items to the item pool.
    """
    display_name = "Toggle Max Life Increase Items"

class InitBombsLimit(Range):
    """
    Limit on the maximum amount of bombs that the player can have.
    """
    display_name = "Bomb Limit"

    range_start = 0
    range_end = 7
    default = 7

class MaxBombItem(Toggle):
    """
    Allow the previous maximum limit on bombs to be able to be increased via items.
    Adds new items to the item pool.
    """
    display_name = "Toggle Max Bomb Increase Items"

class DeathLink(Toggle):
    """
    When you die, everyone else with death link enabled also dies. Same goes the other way. 
    Can be changed later.
    """
    display_name = "Toggle Death Link"

class DeathLinkTrigger(Choice):
    """
    When a DeathLink is triggered. 
    Life: Activate death link upon losing a life.
    Game Over: Activate death link upon getting a game over.
    Can be changed later.
    """
    display_name = "Death Link Trigger"
    option_life = 0
    option_game_over = 1
    default = 0

class DeathLinkAmnesty(Range):
    """
    Number of DeathLink triggers needed before sending a DeathLink. 
    Can be changed later.
    """
    display_name = "DeathLink Amnesty"
    range_start = 1
    range_end = 10
    default = 1

class RingLink(Toggle):
    """
    Enable RingLink. This makes your gain/loss of funds linked to other players.
    Can be changed later.
    """
    display_name = "Toggle Ring Link"

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
    stage_unlock: StageUnlock
    new_card_per_shop: GuaranteeUnpurchasedCardPerShop
    extra_stage: ExtraStage
    magatama_req: MagatamaRequirement
    blank_card_req: BlankCardRequirement
    goal: Goal
    ending_req: EndingsRequired
    card_req: CardsRequired
    difficulty_check: DifficultyCheck
    check_mult_difficulties: CheckMultipleDifficulty
    exclude_lunatic: ExcludeLunatic
    init_max_lives: InitLivesLimit
    max_life_item: MaxLifeItem
    init_max_bombs: InitBombsLimit
    max_bomb_item: MaxBombItem
    deathlink: DeathLink
    deathlink_trigger: DeathLinkTrigger
    deathlink_amnesty: DeathLinkAmnesty
    ring_link: RingLink

