from __future__ import annotations

import inspect

from ..utils.pmf import PMF


class ResultsBase:
    @classmethod
    def merge(cls, left, right):
        if not (isinstance(left, cls) and isinstance(right, cls)):
            raise TypeError('incorrect class types')

        input_names = [k for k in inspect.signature(cls.__init__).parameters.keys() if k != 'self']

        merged_pmfs = {k: PMF.convolve_many([getattr(left, k), getattr(right, k)]) for k in input_names if isinstance(getattr(left, k), PMF)}

        return cls(
            **merged_pmfs
        )

    def repr_items(self):
        return [f'  {k:30s} - avg: {round(v.mean(), 4):.4f}, std: {round(v.std(), 4):.4f}' for k, v in self.__dict__.items() if isinstance(v, PMF)]


    def __repr__(self) -> str:
        output = [
            f'{self.__class__.__name__}(',
            *self.repr_items(),
            ')',
        ]
        return '\n'.join(output)

    @classmethod
    def combine(cls, results: list[ResultsBase]) -> ResultsBase:
        if not all(isinstance(r, cls) for r in results):
            raise TypeError('incorrect class types')

        input_names = [k for k in inspect.signature(cls.__init__).parameters.keys() if k != 'self']

        merged_pmfs = {k: PMF.convolve_many([getattr(r, k) for r in results]) for k in input_names if isinstance(getattr(results[0], k), PMF)}

        return cls(
            **merged_pmfs
        )


class AttackResults(ResultsBase):
    def __init__(self, damage_dist, mortal_wound_dist, self_wound_dist, total_damage_dist, kills_dist):
        self.damage_dist = damage_dist
        self.mortal_wound_dist = mortal_wound_dist
        self.self_wound_dist = self_wound_dist
        self.total_damage_dist = total_damage_dist
        self.kills_dist = kills_dist

    def repr_items(self):
        return [
            f'  {"Mortal Wounds":20s} - avg: {self.mortal_wound_dist.mean():.4f}, std: {self.mortal_wound_dist.std():.4f}',
            f'  {"Self Wounds":20s} - avg: {self.self_wound_dist.mean():.4f}, std: {self.self_wound_dist.std():.4f}',
            f'  {"Total Damage":20s} - avg: {self.total_damage_dist.mean():.4f}, std: {self.total_damage_dist.std():.4f}',
            f'  {"Kills":20s} - avg: {self.kills_dist.mean():.4f}, std: {self.kills_dist.std():.4f}',
        ]


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
                 extra_automatic_hit_dist: PMF, mortal_wound_dist: PMF, self_wound_dist: PMF) -> None:
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
        return PMF.convolve_many([self.successful_hit_dist, self.extra_automatic_hit_dist])

    @classmethod
    def empty(cls) -> HitPhaseResults:
        """
        Return an empty set of results
        """
        return HitPhaseResults(
            successful_hit_dist=PMF.static(0),
            extra_hit_roll_dist=PMF.static(0),
            extra_automatic_wound_dist=PMF.static(0),
            extra_automatic_hit_dist=PMF.static(0),
            mortal_wound_dist=PMF.static(0),
            self_wound_dist=PMF.static(0),
        )

    def multiply_by(self, other_pmf: PMF) -> HitPhaseResults:
        pmfs: dict = {
            'successful_hit_dist': [],
            'extra_hit_roll_dist': [],
            'extra_automatic_wound_dist': [],
            'extra_automatic_hit_dist': [],
            'mortal_wound_dist': [],
            'self_wound_dist': [],
        }

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            pmfs['successful_hit_dist'].append(PMF.convolve_many([self.successful_hit_dist] * dice_count) * event_prob)
            pmfs['extra_hit_roll_dist'].append(PMF.convolve_many([self.extra_hit_roll_dist] * dice_count) * event_prob)
            pmfs['extra_automatic_wound_dist'].append(PMF.convolve_many([self.extra_automatic_wound_dist] * dice_count) * event_prob)
            pmfs['extra_automatic_hit_dist'].append(PMF.convolve_many([self.extra_automatic_hit_dist] * dice_count) * event_prob)
            pmfs['mortal_wound_dist'].append(PMF.convolve_many([self.mortal_wound_dist] * dice_count) * event_prob)
            pmfs['self_wound_dist'].append(PMF.convolve_many([self.self_wound_dist] * dice_count) * event_prob)

        return HitPhaseResults(**{k: PMF.flatten(pmfs[k]) for k in pmfs})

    def recursive_results(self) -> HitPhaseResults:
        results = self.multiply_by(self.extra_hit_roll_dist)
        results.successful_hit_dist = PMF.static(0)
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

    def multiply_by(self, other_pmf: PMF) -> WoundPhaseResults:
        pmfs: dict = {
            'successful_wound_dist': [],
            'extra_wound_roll_dist': [],
            'extra_automatic_wound_dist': [],
            'mortal_wound_dist': [],
            'self_wound_dist': [],
        }

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            pmfs['successful_wound_dist'].append(PMF.convolve_many([self.successful_wound_dist] * dice_count) * event_prob)
            pmfs['extra_wound_roll_dist'].append(PMF.convolve_many([self.extra_wound_roll_dist] * dice_count) * event_prob)
            pmfs['extra_automatic_wound_dist'].append(PMF.convolve_many([self.extra_automatic_wound_dist] * dice_count) * event_prob)
            pmfs['mortal_wound_dist'].append(PMF.convolve_many([self.mortal_wound_dist] * dice_count) * event_prob)
            pmfs['self_wound_dist'].append(PMF.convolve_many([self.self_wound_dist] * dice_count) * event_prob)

        return WoundPhaseResults(**{k: PMF.flatten(pmfs[k]) for k in pmfs})

    def recursive_results(self) -> WoundPhaseResults:
        results: WoundPhaseResults = self.multiply_by(self.extra_wound_roll_dist)
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
    def multiply_by(self, other_pmf: PMF) -> SavePhaseResults:
        pmfs: dict = {
            'failed_armour_save_dist': [],
        }

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            pmfs['failed_armour_save_dist'].append(PMF.convolve_many([self.failed_armour_save_dist] * dice_count) * event_prob)

        return SavePhaseResults(**{k: PMF.flatten(pmfs[k]) for k in pmfs})

    def __init__(self, failed_armour_save_dist: PMF):
        self.failed_armour_save_dist = failed_armour_save_dist


class DamagePhaseResults(ResultsBase):
    """Holds the results from the armour save phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def multiply_by(self, other_pmf: PMF) -> DamagePhaseResults:
        pmfs: dict = {
            'damage_dist': [],
        }

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            pmfs['damage_dist'].append(PMF.convolve_many([self.damage_dist] * dice_count) * event_prob)

        return DamagePhaseResults(**{k: PMF.flatten(pmfs[k]) for k in pmfs})

    def __init__(self, damage_dist: PMF):
        self.damage_dist = damage_dist


class KillPhaseResults:
    """Holds the results from the kill phase

    Args:
        wounds_dist (PMF): The distribution of successful wounds
        mortal_wound_dist (PMF): The distribution of mortal wounds generated
    """
    def multiply_by(self, other_pmf: PMF) -> KillPhaseResults:
        pmfs: dict = {
            'kill_dist': [],
        }

        for dice_count, event_prob in enumerate(other_pmf.values):
            # If the probability is zero then no-op
            if PMF.is_null_prob(event_prob):
                continue

            pmfs['kill_dist'].append(PMF.convolve_many([self.kill_dist] * dice_count) * event_prob)

        return KillPhaseResults(**{k: PMF.flatten(pmfs[k]) for k in pmfs})

    def __init__(self, kill_dist: PMF):
        self.kill_dist = kill_dist
