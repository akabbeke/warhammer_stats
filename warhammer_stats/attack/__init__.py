"""
Classes related to simulating an attack in Warhammer 40000 9th edition
"""

from __future__ import annotations
from functools import cached_property

from .phases.hit_phase import HitPhase
from .phases.wound_phase import WoundPhase
from .phases.save_phase import SavePhase
from .phases.damage_phase import DamagePhase
from .phases.attacks_phase import AttacksPhase

from ..utils.modifier_collection import ModifierCollection
from ..utils.pmf import PMF, PMFCollection
from ..utils.target import Target
from ..utils.weapon import Weapon

from .results import AttackResults

DEBUG = False
# pylint: disable=R0201,C0302,R0913,R0902,R0903,R0904,R0913


class Attack:
    """Generates the probability distribution for damage dealt from an attack sequence

    Note:
        This can be pretty computaionally expensive to run. Don't go crazy with the number
        attacks and expect it to run quickly.

    Args:
        weapon (Weapon): The weapon being used to make the attack
        target (Target): The target of the the attack

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    def __init__(self, weapon: Weapon, target: Target):
        self.weapon = weapon
        self.target = target

    def _hit_phase(self):
        return HitPhase(self.weapon, self.target, self.modifiers)

    def _wound_phase(self):
        return WoundPhase(self.weapon, self.target, self.modifiers)

    def _save_phase(self):
        return SavePhase(self.weapon, self.target, self.modifiers)

    def _attacks_phase(self):
        return AttacksPhase(self.weapon, self.target, self.modifiers)

    def _damage_phase(self):
        return DamagePhase(self.weapon, self.target, self.modifiers)

    @property
    def modifiers(self) -> ModifierCollection:
        """Return a combined list of modifers for both the weapon and the target"""
        return self.weapon.modifiers + self.target.modifiers

    @cached_property
    def hit_phase_results(self):
        return self._hit_phase().results().with_recursive()

    @cached_property
    def wound_phase_results(self):
        return self._wound_phase().results().with_recursive()

    @cached_property
    def save_phase_results(self):
        return self._save_phase().results()

    @cached_property
    def damage_phase_results(self):
        return self._damage_phase().results()

    @cached_property
    def attacks_phase_results(self):
        return self._attacks_phase().results()

    @cached_property
    def total_successful_hits_dist(self):
        return PMF.convolve_many([
            self.hit_phase_results.successful_hit_dist,
            self.hit_phase_results.extra_automatic_hit_dist,
        ])

    @cached_property
    def actual_wound_phase_results(self):
        return self.wound_phase_results.multiply_by(self.total_successful_hits_dist)

    @cached_property
    def total_successfull_wounds_dist(self):
        return PMF.convolve_many([
            self.actual_wound_phase_results.successful_wound_dist,
            self.actual_wound_phase_results.extra_automatic_wound_dist,
            self.hit_phase_results.extra_automatic_wound_dist
        ])

    @cached_property
    def actual_failed_saves_dist(self):
        return self.save_phase_results.multiply_by(
            self.total_successfull_wounds_dist
        ).failed_armour_save_dist

    @cached_property
    def total_damage_results(self):
        return self.damage_phase_results.multiply_by(
            self.actual_failed_saves_dist
        ).multiply_by(
            self.attacks_phase_results.attack_number_dist
        )

    @cached_property
    def total_mortal_wounds(self):
        return PMF.convolve_many([
            self.hit_phase_results.mortal_wound_dist,
            self.actual_wound_phase_results.mortal_wound_dist,
        ])

    @cached_property
    def total_self_wounds(self):
        return PMF.convolve_many([
            self.hit_phase_results.self_wound_dist,
            self.actual_wound_phase_results.self_wound_dist,
        ])

    def apply_feel_no_pain(self, dist: PMF):
        dists = []
        mod_thresh = self.modifiers.modify_fnp_thresh(self.target.fnp)
        for dice, event_prob in enumerate(dist.values):
            if PMF.is_null_prob(event_prob):
                continue
            dice_dists = self.modifiers.modify_fnp_dice(
                PMFCollection.mdn(dice, 6),
                self.target.fnp,
                mod_thresh,
            )
            binom_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)

    @cached_property
    def final_damage_dist(self):
        return self.apply_feel_no_pain(self.total_damage_results.damage_dist).ceiling(self.target.wounds)

    @cached_property
    def final_mortal_wound_dist(self):
        return self.apply_feel_no_pain(self.total_mortal_wounds)

    @cached_property
    def final_self_wound_dist(self):
        return self.apply_feel_no_pain(self.total_self_wounds)

    @cached_property
    def final_total_damage_dist(self):
        return PMF.convolve_many([
            self.final_damage_dist,
            self.final_mortal_wound_dist,
        ])

    def run(self):
        """
        Generate the resulting PMF
        """
        return AttackResults(self.final_damage_dist, self.final_mortal_wound_dist, self.final_self_wound_dist, self.final_total_damage_dist)


class AttackKills:
    """Generates the probability distribution for damage dealt from an attack sequence

    Note:
        This can be pretty computaionally expensive to run. Don't go crazy with the number
        attacks and expect it to run quickly.

    Args:
        weapon (Weapon): The weapon being used to make the attack
        target (Target): The target of the the attack

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    def __init__(self, weapon: Weapon, target: Target):
        self.weapon = weapon
        self.target = target

    def _hit_phase(self):
        return HitPhase(self.weapon, self.target, self.modifiers)

    def _wound_phase(self):
        return WoundPhase(self.weapon, self.target, self.modifiers)

    def _save_phase(self):
        return SavePhase(self.weapon, self.target, self.modifiers)

    def _attacks_phase(self):
        return AttacksPhase(self.weapon, self.target, self.modifiers)

    def _damage_phase(self):
        return DamagePhase(self.weapon, self.target, self.modifiers)

    @property
    def modifiers(self) -> ModifierCollection:
        """Return a combined list of modifers for both the weapon and the target"""
        return self.weapon.modifiers + self.target.modifiers

    @cached_property
    def hit_phase_results(self):
        return self._hit_phase().results().with_recursive()

    @cached_property
    def wound_phase_results(self):
        return self._wound_phase().results().with_recursive()

    @cached_property
    def save_phase_results(self):
        return self._save_phase().results()

    @cached_property
    def damage_phase_results(self):
        return self._damage_phase().results()

    @cached_property
    def attacks_phase_results(self):
        return self._attacks_phase().results()

    @cached_property
    def total_successful_hits_dist(self):
        return PMF.convolve_many([
            self.hit_phase_results.successful_hit_dist,
            self.hit_phase_results.extra_automatic_hit_dist,
        ])

    @cached_property
    def actual_wound_phase_results(self):
        return self.wound_phase_results.multiply_by(self.total_successful_hits_dist)

    @cached_property
    def total_successfull_wounds_dist(self):
        return PMF.convolve_many([
            self.actual_wound_phase_results.successful_wound_dist,
            self.actual_wound_phase_results.extra_automatic_wound_dist,
            self.hit_phase_results.extra_automatic_wound_dist
        ])

    @cached_property
    def actual_failed_saves_dist(self):
        return self.save_phase_results.multiply_by(
            self.total_successfull_wounds_dist
        ).failed_armour_save_dist

    @cached_property
    def total_damage_results(self):
        return self.damage_phase_results.multiply_by(
            self.actual_failed_saves_dist
        ).multiply_by(
            self.attacks_phase_results.attack_number_dist
        )

    @cached_property
    def total_mortal_wounds(self):
        return PMF.convolve_many([
            self.hit_phase_results.mortal_wound_dist,
            self.actual_wound_phase_results.mortal_wound_dist,
        ])

    @cached_property
    def total_self_wounds(self):
        return PMF.convolve_many([
            self.hit_phase_results.self_wound_dist,
            self.actual_wound_phase_results.self_wound_dist,
        ])

    def apply_feel_no_pain(self, dist: PMF):
        dists = []
        mod_thresh = self.modifiers.modify_fnp_thresh(self.target.fnp)
        for dice, event_prob in enumerate(dist.values):
            if PMF.is_null_prob(event_prob):
                continue
            dice_dists = self.modifiers.modify_fnp_dice(
                PMFCollection.mdn(dice, 6),
                self.target.fnp,
                mod_thresh,
            )
            binom_dists = dice_dists.convert_binomial_less_than(mod_thresh).convolve()
            dists.append(binom_dists * event_prob)
        return PMF.flatten(dists)

    @cached_property
    def final_damage_dist(self):
        return self.apply_feel_no_pain(self.total_damage_results.damage_dist).ceiling(self.target.wounds)

    @cached_property
    def final_mortal_wound_dist(self):
        return self.apply_feel_no_pain(self.total_mortal_wounds)

    @cached_property
    def final_self_wound_dist(self):
        return self.apply_feel_no_pain(self.total_self_wounds)

    @cached_property
    def final_total_damage(self):
        return PMF.convolve_many([
            self.final_damage_dist,
            self.final_mortal_wound_dist,
        ])

    def run(self):
        """
        Generate the resulting PMF
        """
        return self.final_total_damage
