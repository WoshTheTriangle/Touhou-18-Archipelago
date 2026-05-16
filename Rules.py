from BaseClasses import CollectionState
from worlds.generic.Rules import add_rule, set_rule

from rule_builder.rules import Has, HasAll, HasAny, Rule
from rule_builder.options import OptionFilter


def set_all_rules(world) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world) -> None:
    print("to be added")

def set_all_location_rules(world) -> None:
    print("to be added")

def set_completion_condition(world) -> None:
    # Frogs go mlem mlem, snakes go psbpspsbsb
    # Thanks for comign folks!
    world.set_completion_rule(Has("Sanae")) 