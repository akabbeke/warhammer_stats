from __future__ import annotations

from ...utils.pmf import PMF, PMFCollection
from . import RollBase


class WoundRollBase(RollBase):
    def split_generator(self):
        return self.modifiers.split_wound_roll(
            self.hit_dice_dists(self.modifiers).convolve(),
            self.hit_thresh_modifier(self.modifiers),
        )


class SuccessfulWoundRoll(WoundRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        # Calculate the exploding dice distributions
        return self.wound_dice_dists(modifiers).convert_binomial(self.wound_thresh_modifiable(modifiers)).convolve()


class ExtraAutomaticWoundRoll(WoundRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.wound_generated_extra_automatic_wound_dist_modifiable().roll(self.wound_thresh_modifier(modifiers)),
            modifiers.wound_generated_extra_automatic_wound_dist_unmodifiable(),
        ]).convolve()


class ExtraWoundRollRoll(WoundRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.extra_wound_roll_dist_modifiable().roll(self.wound_thresh_modifier(modifiers)),
            modifiers.extra_wound_roll_dist_unmodifiable(),
        ]).convolve()


class MortalWoundRoll(WoundRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.wound_generated_mortal_wounds_dist_modifiable().roll(self.wound_thresh_modifier(modifiers)),
            modifiers.wound_generated_mortal_wounds_dist_unmodifiable(),
        ]).convolve()


class SelfWoundRoll(WoundRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        thresh_self_wounds = modifiers.wound_self_wound_thresh()
        if thresh_self_wounds:
            self_thresh = max(thresh_self_wounds + self.wound_thresh_modifier(modifiers), 0)
            return self.dice_dists(modifiers).convert_binomial_less_than(self_thresh).convolve()
        else:
            return PMF.static(0)
