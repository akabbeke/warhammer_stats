from __future__ import annotations

from .roll import RollBase
from ...utils.pmf import PMF, PMFCollection

class DamageRollBase(RollBase):
    def split_generator(self):
        return self.modifiers.split_damage_roll(
            self.hit_dice_dists(self.modifiers).convolve(),
            self.hit_thresh_modifier(self.modifiers),
            self.wound_dice_dists(self.modifiers).convolve(),
            self.wound_thresh_modifier(self.modifiers)
        )


class DamageRoll(DamageRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        # Apply modifiers to the damage distribution
        return modifiers.modify_damage_dice(self.weapon.damage).convolve().ceiling(self.target.wounds)


class FeelNoPainRoll(DamageRollBase):
    def calc_sub_dist(self, modifiers) -> PMF:
        # Apply modifiers to the damage distribution
        return modifiers.modify_damage_dice(self.weapon.damage).convolve()

    def _calc_fnp_dist(self, dist: PMF, modifiers) -> PMF:
        dists = []
        mod_thresh = modifiers.modify_fnp_thresh(self.target.fnp)
        for dice, event_prob in enumerate(dist.values):
            if PMF.is_null_prob(event_prob):
                continue
            dice_dists = modifiers.modify_fnp_dice(
                PMFCollection.mdn(dice, 6),
                self.target.fnp,
                mod_thresh,
            )
            binom_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)
