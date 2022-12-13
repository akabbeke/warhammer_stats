from __future__ import annotations

from functools import cached_property

from ..utils.modifier_collection import ModifierCollection
from ..utils.pmf import PMF, PMFCollection
from ..utils.target import Target
from ..utils.weapon import Weapon
from .phases.attacks_phase import AttacksPhase
from .phases.damage_phase import DamagePhase
from .phases.hit_phase import HitPhase
from .phases.save_phase import SavePhase
from .phases.wound_phase import WoundPhase
from .phases.kill_phase import KillPhase
from .results import AttackResults

DEBUG = False
# pylint: disable=R0201,C0302,R0913,R0902,R0903,R0904,R0913


class Attack:
    """Generates the probability distribution for damage dealt from an attack sequence

    Note:
        This can be pretty computationally expensive to run. Don't go crazy with the number
        attacks and expect it to run quickly.

    Args:
        weapon (Weapon): The weapon being used to make the attack
        target (Target): The target of the the attack

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """
    def __init__(self, weapon: Weapon, target: Target) -> None:
        self.weapon = weapon
        self.target = target

    def _hit_phase(self) -> HitPhase:
        return HitPhase(self.weapon, self.target, self.modifiers)

    def _wound_phase(self) -> WoundPhase:
        return WoundPhase(self.weapon, self.target, self.modifiers)

    def _save_phase(self) -> SavePhase:
        return SavePhase(self.weapon, self.target, self.modifiers)

    def _attacks_phase(self) -> AttacksPhase:
        return AttacksPhase(self.weapon, self.target, self.modifiers)

    def _damage_phase(self) -> DamagePhase:
        return DamagePhase(self.weapon, self.target, self.modifiers)

    def _kill_phase(self) -> KillPhase:
        return KillPhase(self.weapon, self.target, self.modifiers)

    @property
    def modifiers(self) -> ModifierCollection:
        """Return a combined list of modifers for both the weapon and the target"""
        return self.weapon.modifiers + self.target.modifiers

    @cached_property
    def hit_phase_results(self) -> AttackResults:
        """Return the results of the hit phase"""
        return self._hit_phase().results().with_recursive()

    @cached_property
    def wound_phase_results(self) -> AttackResults:
        """Return the results of the wound phase"""
        return self._wound_phase().results().with_recursive()

    @cached_property
    def save_phase_results(self) -> AttackResults:
        """Return the results of the save phase"""
        return self._save_phase().results()

    @cached_property
    def damage_phase_results(self) -> AttackResults:
        """Return the results of the damage phase"""
        return self._damage_phase().results()

    @cached_property
    def attacks_phase_results(self) -> AttackResults:
        """Return the results of the attacks phase"""
        return self._attacks_phase().results()

    @cached_property
    def total_successful_hits_dist(self) -> PMF:
        """Return the probability distribution of successful hits"""
        return PMF.convolve_many([
            self.hit_phase_results.successful_hit_dist,
            self.hit_phase_results.extra_automatic_hit_dist,
        ])

    @cached_property
    def total_successful_wounds_dist(self) -> PMF:
        """Return the combined probability distribution of all successful wounds"""
        return PMF.convolve_many([
            self.hit_wound_phase_results.successful_wound_dist,
            self.hit_wound_phase_results.extra_automatic_wound_dist,
            self.hit_phase_results.extra_automatic_wound_dist
        ])

    @cached_property
    def actual_failed_saves_dist(self) -> PMF:
        """Return the probability distribution of failed saves"""
        return self.save_phase_results.multiply_by(
            self.total_successful_wounds_dist
        ).failed_armour_save_dist

    @cached_property
    def hit_wound_phase_results(self) -> AttackResults:
        """Return the results of the wound phase multiplied by the number of successful hits"""
        return self.wound_phase_results.multiply_by(self.total_successful_hits_dist)

    @cached_property
    def total_damage_results(self) -> AttackResults:
        return self.damage_phase_results.multiply_by(
            self.actual_failed_saves_dist
        ).multiply_by(
            self.attacks_phase_results.attack_number_dist
        )

    @cached_property
    def total_mortal_wounds(self) -> PMF:
        return PMF.convolve_many([
            self.hit_phase_results.multiply_by(self.attacks_phase_results.attack_number_dist).mortal_wound_dist,
            self.hit_wound_phase_results.multiply_by(self.attacks_phase_results.attack_number_dist).mortal_wound_dist,
        ])

    @cached_property
    def total_self_wounds(self) -> PMF:
        return PMF.convolve_many([
            self.hit_phase_results.self_wound_dist,
            self.hit_wound_phase_results.self_wound_dist,
        ])

    def apply_feel_no_pain(self, dist: PMF) -> PMF:
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
    def final_damage_dist(self) -> PMF:
        return self.apply_feel_no_pain(self.total_damage_results.damage_dist)

    @cached_property
    def final_mortal_wound_dist(self) -> PMF:
        return self.apply_feel_no_pain(self.total_mortal_wounds)

    @cached_property
    def final_self_wound_dist(self) -> PMF:
        return self.apply_feel_no_pain(self.total_self_wounds)

    @cached_property
    def final_total_damage_dist(self) -> PMF:
        return PMF.convolve_many([
            self.final_damage_dist,
            self.final_mortal_wound_dist,
        ])

    @cached_property
    def kills_dist(self) -> PMF:
        total_successful_hits_dist = PMF.convolve_many([
            self.hit_phase_results.successful_hit_dist,
            self.hit_phase_results.extra_automatic_hit_dist,
        ])

        hit_and_wound_phase_results = self.wound_phase_results.multiply_by(total_successful_hits_dist)

        hit_and_wounds_dist = PMF.convolve_many([
            hit_and_wound_phase_results.successful_wound_dist,
            hit_and_wound_phase_results.extra_automatic_wound_dist,
            self.hit_phase_results.extra_automatic_wound_dist
        ])

        failed_saves_dist = self.save_phase_results.multiply_by(
            hit_and_wounds_dist
        ).multiply_by(
            self.attacks_phase_results.attack_number_dist
        ).failed_armour_save_dist


        damage_dist = self.apply_feel_no_pain(self.damage_phase_results.damage_dist)

        return self._kill_phase().calc_dist(failed_saves_dist, damage_dist, self.final_mortal_wound_dist)

    def run(self):
        """
        Generate the resulting PMF
        """

        return AttackResults(
            self.final_damage_dist,
            self.final_mortal_wound_dist,
            self.final_self_wound_dist,
            self.final_total_damage_dist,
            self.kills_dist,
        )
