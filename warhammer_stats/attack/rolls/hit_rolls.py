from __future__ import annotations

from ...utils.pmf import PMF, PMFCollection
from . import RollBase


class HitRollBase(RollBase):
    def split_generator(self):
        return self.modifiers.split_hit_roll()


class SuccessfulHitRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return self.hit_dice_dists(modifiers).convert_binomial(self.hit_thresh_modifiable(modifiers)).convolve()


class ExtraAutomaticHitRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.extra_automatic_hit_dist_modifiable().roll(self.hit_thresh_modifier(modifiers)),
            modifiers.extra_automatic_hit_dist_unmodifiable(),
        ]).convolve()


class ExtraAutomaticWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.hit_generated_extra_automatic_wound_dist_modifiable().roll(self.hit_thresh_modifier(modifiers)),
            modifiers.hit_generated_extra_automatic_wound_dist_unmodifiable(),
        ]).convolve()


class ExtraHitRollRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.extra_hit_roll_dist_modifiable().roll(self.hit_thresh_modifier(modifiers)),
            modifiers.extra_hit_roll_dist_unmodifiable(),
        ]).convolve()


class MortalWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return PMFCollection.add_many([
            modifiers.hit_generated_mortal_wounds_dist_modifiable().roll(self.hit_thresh_modifier(self.modifiers)),
            modifiers.hit_generated_mortal_wounds_dist_unmodifiable(),
        ]).convolve()


class SelfWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        thresh_self_wounds = modifiers.hit_self_wound_thresh()

        if thresh_self_wounds:
            self_wound_thresh = max(thresh_self_wounds + self.hit_thresh_modifier(modifiers), 0)
            return self.hit_dice_dists().convert_binomial_less_than(self_wound_thresh).convolve()
        else:
            return PMF.static(0)
