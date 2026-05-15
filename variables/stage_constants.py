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

DIFFICULTIES = [DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_LUNATIC, DIFFICULTY_EXTRA]

REIMU_SPEED = [576, 256, 407, 181]
MARISA_SPEED = [640, 256, 452, 181]
SAKUYA_SPEED = [576, 256, 407, 181]
SANAE_SPEED = [576, 256, 407, 181]

CHARACTER_SPEEDS = [REIMU_SPEED, MARISA_SPEED, SAKUYA_SPEED, SANAE_SPEED]


# String constants for location names

DIFFICULTY_NAMES = ["Easy", "Normal", "Hard", "Lunatic"]
CHARCTER_NAMES = ["Reimu", "Marisa", "Sakuya", "Sanae"]

STAGE_CHECKS = [
    ["Mike - MidBoss", "Mike Defeated"],
    ["Takane - MidBoss", "Takane Defeated"],
    ["Sannyo - MidBoss", "Sannyo Defeated"],
    ["Yin-Yang Wheel - MidBoss", "Misumaru Defeated"],
    ["Tsukasa - MidBoss 1", "Megumu Defeated"],
    ["Tsukasa - MidBoss 2", "Chimata Defeated"],
    ["Tsukasa - MidBoss 3", "Momoyo Defeated"]
]