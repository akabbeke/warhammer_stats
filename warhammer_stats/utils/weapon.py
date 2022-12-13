"""
Classes for representing an attacking weapon
"""

from .pmf import PMFCollection
from .modifier_collection import ModifierCollection

from typing import Optional

# pylint: disable=too-many-arguments,too-few-public-methods

class Weapon:
    """
    Holds the params of a weapon
    """
    def __init__(self, bs: int, shots: PMFCollection, strength: int, ap: int,
                 damage: PMFCollection, modifiers: Optional[ModifierCollection] = None,
                 name: Optional[str] = None, cost: Optional[float] = None) -> None:
        self.bs = bs  # pylint: disable=invalid-name
        self.shots = shots
        self.strength = strength
        self.ap = ap  # pylint: disable=invalid-name
        self.damage = damage
        self.modifiers = modifiers or ModifierCollection()
        self.name = name
        self.cost = cost
