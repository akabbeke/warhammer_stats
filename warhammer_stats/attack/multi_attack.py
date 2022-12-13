from .attack import Attack
from ..utils.target import Target
from ..utils.weapon import Weapon

from .results import AttackResults

from functools import cache


class MultiAttack:
    def __init__(self, weapons: list[Weapon], target: Target) -> None:
        self.weapons = weapons
        self.target = target
    
    @cache
    def run_attack(self, weapon: Weapon, target: Target) -> Attack:
        return Attack(weapon, target).run()
    
    def run(self) -> AttackResults:
        results = []
        for weapon in self.weapons:
            results.append(self.run_attack(weapon, self.target))

        return AttackResults.combine(results)
