"""
Defins the Species class which is an enum 
of all possible species of flowers in AC:NH.

Possible options are: 
Rose, Tulip, Pansy, Cosmos, Lily, 
Hyacinth, Windflower, and Mum. 
"""
from enum import Enum, auto

class Species(Enum):
    ROSE = auto()
    TULIP = auto()
    PANSY = auto()
    COSMOS = auto()
    LILY = auto()
    HYACINTH = auto()
    WINDFLOWER = auto()
    MUM = auto()
