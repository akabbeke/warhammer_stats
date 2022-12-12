from __future__ import annotations

from ...utils.pmf import PMF
from .roll import RollBase


class SaveRollBase(RollBase):
    def split_generator(self):
        return self.modifiers.split_save_roll(
            self.hit_dice_dists(self.modifiers).convolve(),
            self.hit_thresh_modifier(self.modifiers),
            self.wound_dice_dists(self.modifiers).convolve(),
            self.wound_thresh_modifier(self.modifiers)
        )


class FailedArmourSaveRoll(SaveRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return self.save_dice_dists(modifiers).convert_binomial_less_than(self.save_thresh_modifiable(modifiers)).convolve()
