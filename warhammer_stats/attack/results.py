from __future__ import annotations

import inspect

from ..utils.pmf import PMF


class ResultsBase:
    def multiply_by(self, other_pmf: PMF) -> ResultsBase:
        input_names = [k for k in inspect.signature(self.__class__.__init__).parameters.keys() if k != 'self']

        pmfs = {k: [] for k in input_names if isinstance(getattr(self, k), PMF)}

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            for input_name in input_names:
                pmfs[input_name].append(PMF.convolve_many([getattr(self, input_name)] * dice_count) * event_prob)

        flattened_pmfs = {k: PMF.flatten(pmfs[k]) for k in pmfs}
        return self.__class__(**flattened_pmfs)

    @classmethod
    def merge(cls, left, right):
        if not (isinstance(left, cls) and isinstance(right, cls)):
            raise TypeError('incorrect class types')

        input_names = [k for k in inspect.signature(cls.__init__).parameters.keys() if k != 'self']

        merged_pmfs = {k: PMF.convolve_many([getattr(left, k), getattr(right, k)]) for k in input_names if isinstance(getattr(left, k), PMF)}

        return cls(
            **merged_pmfs
        )

class AttackResults:
    def __init__(self, damage_dist, mortal_wound_dist, self_wound_dist, total_damage_dist):
        self.damage_dist = damage_dist
        self.mortal_wound_dist = mortal_wound_dist
        self.self_wound_dist = self_wound_dist
        self.total_damage_dist = total_damage_dist


class AttacksPhaseResults:
    """Holds the results of determining the number of attacks.

    Args:
        shot_dist (PMF): The distribution of shots to be made
    """
    def __init__(self, attack_number_dist: PMF):
        self.attack_number_dist = attack_number_dist


class HitPhaseResults(ResultsBase):
    """Holds the results from the to hit phase of the attack

    Args:
        hit_dist (PMF): The distribution of successful hits
        exploding_dice_dists (PMF): The distribution of successful hits generated from
            exploding dice
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
        self_inflicted_dist (PMF): The distribution of wounds inflicted on the attacker
    """
    def __init__(self, successful_hit_dist: PMF, extra_hit_roll_dist: PMF, extra_automatic_wound_dist: PMF,
                 extra_automatic_hit_dist: PMF, mortal_wound_dist: PMF, self_wound_dist: PMF):
        self.successful_hit_dist = successful_hit_dist
        self.extra_hit_roll_dist = extra_hit_roll_dist
        self.extra_automatic_wound_dist = extra_automatic_wound_dist
        self.extra_automatic_hit_dist = extra_automatic_hit_dist
        self.mortal_wound_dist = mortal_wound_dist
        self.self_wound_dist = self_wound_dist

    @property
    def combined_hit_dists(self) -> PMF:
        """
        The combined damage distribution from the hit and exploding wounds
        """
        return PMF.convolve_many([self.hit_dist, self.exploding_dice_dist])

    @classmethod
    def empty(cls) -> HitPhaseResults:
        """
        Return an empty set of results
        """
        return HitPhaseResults(
            hit_dist=PMF.static(0),
            exploding_dice_dist=PMF.static(0),
            mortal_wound_dist=PMF.static(0),
            self_inflicted_dist=PMF.static(0),
            wound_dist=PMF.static(0),
        )

    def recursive_results(self) -> HitPhaseResults:
        results = self.multiply_by(self.extra_hit_roll_dist)
        results.extra_hit_roll_dist = PMF.static(0)
        results.extra_automatic_hit_dist = PMF.static(0)
        results.extra_automatic_wound_dist = PMF.static(0)
        return results

    def with_recursive(self):
        return self.merge(self, self.recursive_results())


class WoundPhaseResults(ResultsBase):
    """Holds the results from the to wound phase of the attack

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, successful_wound_dist: PMF, extra_wound_roll_dist: PMF, extra_automatic_wound_dist: PMF,
                 mortal_wound_dist: PMF, self_wound_dist: PMF):
        self.successful_wound_dist = successful_wound_dist
        self.extra_wound_roll_dist = extra_wound_roll_dist
        self.extra_automatic_wound_dist = extra_automatic_wound_dist
        self.mortal_wound_dist = mortal_wound_dist
        self.self_wound_dist = self_wound_dist

    def recursive_results(self) -> WoundPhaseResults:
        results = self.multiply_by(self.extra_wound_roll_dist)
        results.extra_wound_roll_dist = PMF.static(0)
        results.extra_automatic_wound_dist = PMF.static(0)
        return results

    def with_recursive(self):
        return self.merge(self, self.recursive_results())


class SavePhaseResults(ResultsBase):
    """Holds the results from the armour save phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, failed_armour_save_dist: PMF):
        self.failed_armour_save_dist = failed_armour_save_dist


class DamagePhaseResults(ResultsBase):
    """Holds the results from the armour save phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, damage_dist: PMF):
        self.damage_dist = damage_dist


class KillPhaseResults:
    """Holds the results from the kill phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def __init__(self, kill_dist: PMF):
        self.kill_dist = kill_dist
