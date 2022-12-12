from __future__ import annotations

from .phase import PhaseBase
from ..results import DamagePhaseResults

from ..rolls.damage_roll import DamageRoll


class DamagePhase(PhaseBase):
    def results(self) -> DamagePhaseResults:
        return DamagePhaseResults(
            damage_dist=self.damage_roll.calc_dist(),
        )

    @property
    def damage_roll(self):
        return DamageRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )
