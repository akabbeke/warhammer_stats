from __future__ import annotations

from ...utils.pmf import PMF, PMFCollection
from .roll import RollBase


class HitRollBase(RollBase):
    def split_generator(self):
        return self.modifiers.split_hit_roll()


class SuccessfulHitRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        return self.hit_dice_dists(modifiers).convert_binomial(self.hit_thresh_modifiable(modifiers)).convolve()


class ExtraAutomaticHitRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        hit_dist = self.hit_dice_dists(modifiers).convolve()
        return PMFCollection([
            modifiers.extra_automatic_hit_dist_modifiable().mul_pmf(hit_dist.roll(self.hit_thresh_modifier(self.modifiers))),
            modifiers.extra_automatic_hit_dist_unmodifiable().mul_pmf(hit_dist),
        ]).convolve()


class ExtraAutomaticWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        hit_dist = self.hit_dice_dists(modifiers).convolve()
        return PMFCollection([
            modifiers.hit_generated_extra_automatic_wound_dist_modifiable().mul_pmf(hit_dist.roll(self.hit_thresh_modifier(self.modifiers))),
            modifiers.hit_generated_extra_automatic_wound_dist_unmodifiable().mul_pmf(hit_dist),
        ]).convolve()


class ExtraHitRollRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        hit_dist = self.hit_dice_dists(modifiers).convolve()
        return PMFCollection([
            modifiers.extra_hit_roll_dist_modifiable().mul_pmf(hit_dist.roll(self.hit_thresh_modifier(self.modifiers))),
            modifiers.extra_hit_roll_dist_unmodifiable().mul_pmf(hit_dist),
        ]).convolve()


class MortalWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        hit_dist = self.hit_dice_dists(modifiers).convolve()
        return PMFCollection([
            modifiers.hit_generated_mortal_wounds_dist_modifiable().mul_pmf(hit_dist.roll(self.hit_thresh_modifier(self.modifiers))),
            modifiers.hit_generated_mortal_wounds_dist_unmodifiable().mul_pmf(hit_dist),
        ]).convolve()


class SelfWoundRoll(HitRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        thresh_self_wounds = modifiers.hit_self_wound_thresh()

        if thresh_self_wounds:
            self_wound_thresh = max(thresh_self_wounds + self.hit_thresh_modifier(modifiers), 0)
            return self.hit_dice_dists(modifiers).convert_binomial_less_than(self_wound_thresh).convolve()
        else:
            return PMF.static(0)
