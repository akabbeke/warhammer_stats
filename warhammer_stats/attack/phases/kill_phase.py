from __future__ import annotations

import math
from collections import defaultdict
from functools import cache

from ...utils.pmf import PMF
from .phase import PhaseBase


def get_max_depth(wounds: int, dice: int, dam_pmf: PMF) -> int:
    """Returns the maximum number of dice rolls"""
    for damage, damage_prob in enumerate(dam_pmf.values):
        if not PMF.is_null_prob(damage_prob):
            if damage == 0:
                return dice
            return math.ceil(wounds/damage)
    return 0


@cache
def generate_kill_tree(wounds: int, dice: int, damage_pmf: PMF, mortals_pmf: PMF) -> list[tuple[int, float]]:
    """Generates the tree composed of the one-kill trees"""
    if dice <= 0:
        return [(0, 1)]
    else:
        kills = []
        max_depth = get_max_depth(wounds, dice, damage_pmf)
        dice_dist, zeros_dist = generate_one_kill_tree(wounds, min(dice, max_depth), damage_pmf)
        for dice_used, dice_prob in dice_dist:
            kills += [(x[0] + 1, x[1] * dice_prob) for x in generate_kill_tree(wounds, dice - dice_used, damage_pmf, mortals_pmf)]
        for dice_used, dice_prob, wounds_left in zeros_dist:
            if (dice - dice_used) != 0:
                raise Exception("Zeros when not all dice used")
            kills += [(x[0], x[1] * dice_prob) for x in generate_mortal_kill_tree(wounds, wounds_left, mortals_pmf)]
        return normalize_tree(kills)


@cache
def generate_mortal_kill_tree(wounds: int, wounds_left: int, mortal_pmf: PMF) -> list[tuple[int, float]]:
    """Generates the tree composed of the one-kill trees"""
    kills = []

    for damage, damage_prob in enumerate(mortal_pmf.values):
        if PMF.is_null_prob(damage_prob):
            continue
        if damage < wounds_left:
            kills.append((0, damage_prob))
        elif damage == wounds_left:
            kills.append((1, damage_prob))
        else:
            kills.append((1 + wounds//(damage - wounds_left), damage_prob))
    return normalize_tree(kills)


@cache
def generate_one_kill_tree(wounds: int, depth: int, damage_pmf: PMF) -> tuple[list[tuple[int, float]], list[tuple[int, float, int]]]:
    """Generate the tree for the probability of dice required to get a single kill
    """
    # The damages and kills lists are a list of pairs where the
    damages = []
    zeros = []
    if wounds <= 0:
        damages.append((0, 1.0))
    elif depth == 0:
        zeros.append((0, 1.0, wounds))
    else:
        actual_damage_pmf = damage_pmf.ceiling(wounds)
        for damage, damage_prob in enumerate(actual_damage_pmf.values):
            if PMF.is_null_prob(damage_prob):
                continue
            tree_dam, tree_zeros = generate_one_kill_tree(wounds - damage, depth - 1, damage_pmf)
            damages += [(x[0] + 1, float(x[1] * damage_prob)) for x in tree_dam]
            zeros += [(x[0] + 1, float(x[1] * damage_prob), x[2]) for x in tree_zeros]
        damages = normalize_tree(damages)
        zeros = normalize_tree_zeros(zeros)
    return damages, zeros


def tree_to_pmf(tree: list[tuple[int, float]]) -> PMF:
    """Flattens the tree results into a single list
    """
    tree_values: defaultdict = defaultdict(int)
    for dice_needed, probability in tree:
        tree_values[dice_needed] += probability
    values = [0.0] * (1 + max(tree_values.keys()))
    for k in tree_values:
        values[k] = tree_values[k]
    return PMF(values)


def normalize_tree(tree: list[tuple[int, float]]) -> list[tuple[int, float]]:
    tree_values: defaultdict = defaultdict(int)
    for dice_needed, probability in tree:
        tree_values[dice_needed] += probability
    return [(k, tree_values[k]) for k in sorted(tree_values.keys())]


def normalize_tree_zeros(tree: list[tuple[int, float, int]]) -> list[tuple[int, float, int]]:
    tree_values: defaultdict = defaultdict(int)
    for dice_needed, probability, wounds_left in tree:
        tree_values[(dice_needed, wounds_left)] += probability
    return [(k[0], tree_values[k], k[1])for k in sorted(tree_values.keys())]


@cache
def calculate_kills(wounds: int, dice: int, dam_pmf: PMF, mortal_pmf: PMF) -> PMF:
    kill_tree = generate_kill_tree(wounds, dice, dam_pmf, mortal_pmf)
    return tree_to_pmf(kill_tree)


class KillPhase(PhaseBase):
    """
    Generate the PMF for the kills dealt to the target
    """

    def calc_dist(self, dist: PMF, damage_dist: PMF, mortal_wound_dist: PMF) -> PMF:
        """Calculate the probability distribution of the number of kills from a
        failed saving throw. This accounts for feel no pain, target wounds characteristic
        and other damage modifiers.
        """

        damage_dists = []
        for dice, event_prob in enumerate(dist.values):
            if PMF.is_null_prob(event_prob):
                continue
            damage_dists.append(calculate_kills(self.target.wounds, dice, damage_dist, mortal_wound_dist) * event_prob)

        return PMF.flatten(damage_dists)
