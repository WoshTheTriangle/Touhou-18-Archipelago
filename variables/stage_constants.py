from .address_shop import *

'''
General IDs
This connects the shop card addresses and the IDs of the cards when held.
'''

CHARACTER_REIMU = 0
CHARACTER_MARISA = 1
CHARACTER_SAKUYA = 2
CHARACTER_SANAE = 3

CHARACTERS = [CHARACTER_REIMU, CHARACTER_MARISA, CHARACTER_SAKUYA, CHARACTER_SANAE]

DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_LUNATIC = 3
DIFFICULTY_EXTRA = 4

IN_STAGE = 0
IN_MENU = 1
IN_SHOP = 2

DIFFICULTIES = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_LUNATIC, DIFFICULTY_EXTRA]

REIMU_SPEED = [576, 256, 407, 181]
MARISA_SPEED = [640, 256, 452, 181]
SAKUYA_SPEED = [576, 256, 407, 181]
SANAE_SPEED = [576, 256, 407, 181]

CHARACTER_SPEEDS = [REIMU_SPEED, MARISA_SPEED, SAKUYA_SPEED, SANAE_SPEED]


# String constants for location names

DIFFICULTY_NAMES = ["Easy", "Normal", "Hard", "Lunatic"]
CHARACTER_NAMES = ["Reimu", "Marisa", "Sakuya", "Sanae"]
CHARACTER_NAMES_TO_ID = {"Reimu": 0, "Marisa": 1, "Sakuya": 2, "Sanae": 3}

STAGE_CHECKS = [
    ["Mike - MidBoss", "Mike Defeated"],
    ["Takane - MidBoss", "Takane Defeated"],
    ["Sannyo - MidBoss", "Sannyo Defeated"],
    ["Yin-Yang Wheel - MidBoss", "Misumaru Defeated"],
    ["Tsukasa - MidBoss 1", "Megumu Defeated"],
    ["Tsukasa - MidBoss 2", "Chimata Defeated"],
    ["Tsukasa - MidBoss 3", "Momoyo Defeated"]
]

EXTRA_CHECKS = ["Tsukasa - MidBoss 3", "Momoyo Defeated"]

SPELLCARD_COUNT_PER_STAGE = [8, 12, 12, 12, 16, 24, 13]

STAGE_GLOBAL = 0
STAGE_PER_CHARACTER = 2

EXTRA_LINEAR = 0
EXTRA_APART = 1
EXTRA_CARD_REQ = 2
EXTRA_NOT_INCLUDED = 3

GOAL_CHIMATA = 0
GOAL_MOMOYO = 1
GOAL_CHIMATA_BLANK = 2
GOAL_ITEMS = 3
GOAL_ALL = 4

DEATHLINK_TRIGGER_LIFE = 0
DEATHLINK_TRIGGER_GAMEOVER = 1