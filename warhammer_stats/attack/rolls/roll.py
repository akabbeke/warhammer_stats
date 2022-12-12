from __future__ import annotations

from ...utils.modifier_collection import ModifierCollection
from ...utils.pmf import PMF, PMFCollection
from ...utils.target import Target
from ...utils.weapon import Weapon

class RollBase:
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
        self._thresh_mod = None

    def calc_dist(self) -> PMF:
        dists = []
        for prob, modifiers in self.split_generator():
            dists.append(self.calc_sub_dist(modifiers) * prob)
        return PMF.flatten(dists)

    def split_generator(self):
        return [[1.0, self.modifiers]]

    def calc_sub_dist(self, modifiers) -> PMF:
        return PMF.static(0)

    # Hit Dice
    def hit_dice_dists(self, modifiers) -> PMFCollection:
        """Calculate the probability distribution of the number of successful hits in
        in the attack phase. This takes into account modifiers and other effects as
        extra hits and shots.
        """
        # The bare threshold to hit is the weapons to hit value
        thresh = self.weapon.bs

        # Create a dice distribution for 'dice_count' d6 dice
        dice_dists = PMFCollection.mdn(1, 6)

        # Apply modifiers to the dice distribution
        return self.modifiers.modify_hit_dice(dice_dists, thresh, self.hit_thresh_modifiable(modifiers))

    def hit_thresh_modifiable(self, modifiers) -> int:
        return modifiers.modify_hit_thresh(self.weapon.bs)

    def hit_thresh_modifier(self, modifiers):
        # This is a bit of a hack to get the delta between the threshold and the modified threshold
        return modifiers.modify_hit_thresh(6) - 6

    # Wound Dice
    def wound_dice_dists(self, modifiers) -> PMFCollection:
        """Calculate the probability distribution of the number of successful hits in
        in the attack phase. This takes into account modifiers and other effects as
        extra hits and shots.
        """

        # Apply modifiers to the dice distribution
        return modifiers.modify_wound_dice(
            PMFCollection.mdn(1, 6),
            self.wound_thresh(modifiers),
            self.wound_thresh_modifiable(modifiers)
        )

    def wound_thresh(self, modifiers) -> int:
        return self.calc_wound_thresh(
            modifiers.modify_weapon_strength(self.weapon.strength),
            modifiers.modify_target_toughness(self.target.toughness),
        )

    def wound_thresh_modifiable(self, modifiers) -> int:
        return modifiers.modify_wound_thresh(self.wound_thresh(modifiers))

    def wound_thresh_modifier(self, modifiers):
        # This is a bit of a hack to get the delta between the threshold and the modified threshold
        return modifiers.modify_wound_thresh(6) - 6

    def calc_wound_thresh(self, strength: int, toughness: int) -> int:
        # Generate the wound threshold
        if strength <= toughness/2.0:  # pylint: disable=no-else-return
            # If the toughness is greater than twice the strength wound on a 6+
            return 6
        elif strength >= toughness*2:
            # If the stength is greater than twice the toughness wound on a 2+
            return 2
        elif toughness > strength:
            # Else if toughness is greater than strength wound on a 5_
            return 5
        elif toughness == strength:
            # Else if they are equal then wound on a 4+
            return 4
        else:
            # If the strength is greater than toughness wound on a 3+
            return 3

    # Save Dice
    def save_dice_dists(self, modifiers) -> PMFCollection:
        dice_dists = PMFCollection.mdn(1, 6)
        return modifiers.modify_save_dice(
            dice_dists,
            self.save_thresh_modifiable(modifiers),
            self.save_thresh_modifiable(modifiers),
        )

    def save_thresh_modifiable(self, modifiers) -> int:
        return modifiers.modify_pen_thresh(
            self.target.save,
            self.weapon.ap,
            self.target.invuln
        )
