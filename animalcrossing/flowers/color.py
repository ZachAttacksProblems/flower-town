"""
Module which defines an Enum of all possible
flower colors in Animal Crossing: New Horizons.

Inherits Enum and has the following nine (9) colors:
Blue, Red, Yellow, White, Pink, Orange, Purple, Black, and Green.
Their ordering is arbitrary.
"""
from enum import Enum, auto


class FlowerColor(Enum):
    BLUE = auto()
    RED = auto()
    YELLOW = auto()
    WHITE = auto()
    PINK = auto()
    ORANGE = auto()
    PURPLE = auto()
    BLACK = auto()
    GREEN = auto()
