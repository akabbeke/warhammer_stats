from .phase import PhaseBase
from ..results import WoundPhaseResults
from ..rolls.wound_rolls import (SuccessfulWoundRoll, ExtraWoundRollRoll, ExtraAutomaticWoundRoll, MortalWoundRoll, SelfWoundRoll)


class WoundPhase(PhaseBase):
    def results(self):
        return WoundPhaseResults(
            successful_wound_dist=self.successful_wound_roll.calc_dist(),
            extra_wound_roll_dist=self.extra_wound_roll_roll.calc_dist(),
            extra_automatic_wound_dist=self.extra_automatic_wound_roll.calc_dist(),
            mortal_wound_dist=self.mortal_wound_roll.calc_dist(),
            self_wound_dist=self.self_wound_roll.calc_dist(),
        )

    @property
    def successful_wound_roll(self):
        return SuccessfulWoundRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )

    @property
    def extra_wound_roll_roll(self):
        return ExtraWoundRollRoll(
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
