"""
Classes related to modeling the target of an attack
"""

from .modifier_collection import ModifierCollection

from typing import Optional

# pylint: disable=too-many-arguments,too-few-public-methods


class Target:
    """
    Holds params of a target
    """
    def __init__(self, toughness: int, save: int, invuln: int, fnp: int, wounds: int,
                 modifiers: Optional[ModifierCollection] = None, name: Optional[str] = None,
                 cost: Optional[float] = None):
        self.toughness = toughness
        self.save = save
        self.invuln = invuln
        self.fnp = fnp
        self.wounds = wounds
        self.modifiers = modifiers or ModifierCollection()
        self.name = name
        self.cost = cost
