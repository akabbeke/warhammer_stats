from __future__ import annotations

from ...utils.modifier_collection import ModifierCollection
from ...utils.pmf import PMFCollection
from ...utils.target import Target
from ...utils.weapon import Weapon

from typing import Optional

class PhaseBase:
    """The base class for attack segments

    Note:
        This is just a base class that contains a number of common methods

    Args:
        attack (Attack): A reference to the attack being made
    """
    def __init__(self, weapon: Weapon, target: Target, modifiers: ModifierCollection):
        self.weapon = weapon
        self.target = target
        self.modifiers = modifiers
        self._thresh_mod: Optional[int] = None

    @property
    def thresh_mod(self) -> int:
        """
        A cached copy of the threshold modifier
        """
        # cache the threshold modifier
        if self._thresh_mod is None:
            self._thresh_mod = self._get_thresh_mod()
        return self._thresh_mod

    def _get_thresh_mod(self) -> int:
        return 0

    def _mod_extra_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _extra_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _mod_mortal_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()

    def _mortal_dist(self) -> PMFCollection:
        # Stub
        return PMFCollection.empty()
