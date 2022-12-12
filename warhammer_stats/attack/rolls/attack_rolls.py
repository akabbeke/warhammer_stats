from __future__ import annotations

from .roll import RollBase
from ...utils.pmf import PMF


class AttacksRollBase(RollBase):
    pass


class AttackNumberRoll(AttacksRollBase):
    def calc_dist(self) -> PMF:
        return self.modifiers.modify_shot_dice(self.weapon.shots).convolve()
