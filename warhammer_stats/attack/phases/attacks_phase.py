from __future__ import annotations

from .phase import PhaseBase
from ..results import AttacksPhaseResults

from ..rolls.attack_rolls import AttackNumberRoll


class AttacksPhase(PhaseBase):
    def results(self):
        return AttacksPhaseResults(
            attack_number_dist=self.attack_number_roll.calc_dist(),
        )

    @property
    def attack_number_roll(self):
        return AttackNumberRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )
