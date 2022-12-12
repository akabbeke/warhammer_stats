from .phase import PhaseBase
from ..results import HitPhaseResults

from ..rolls.hit_rolls import (SuccessfulHitRoll, ExtraHitRollRoll, ExtraAutomaticWoundRoll, ExtraAutomaticHitRoll, MortalWoundRoll, SelfWoundRoll)

class HitPhase(PhaseBase):
    def results(self):
        return HitPhaseResults(
            successful_hit_dist=self.successful_hit_roll.calc_dist(),
            extra_hit_roll_dist=self.extra_hit_roll_roll.calc_dist(),
            extra_automatic_hit_dist=self.extra_automatic_hit_roll.calc_dist(),
            extra_automatic_wound_dist=self.extra_automatic_wound_roll.calc_dist(),
            mortal_wound_dist=self.mortal_wound_roll.calc_dist(),
            self_wound_dist=self.self_wound_roll.calc_dist(),
        )

    @property
    def successful_hit_roll(self):
        return SuccessfulHitRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def extra_hit_roll_roll(self):
        return ExtraHitRollRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def extra_automatic_wound_roll(self):
        return ExtraAutomaticWoundRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def extra_automatic_hit_roll(self):
        return ExtraAutomaticHitRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def mortal_wound_roll(self):
        return MortalWoundRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def self_wound_roll(self):
        return SelfWoundRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )
