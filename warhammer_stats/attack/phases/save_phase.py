from .phase import PhaseBase
from ..results import SavePhaseResults
from ..rolls.save_rolls import FailedArmourSaveRoll


class SavePhase(PhaseBase):
    def results(self):
        return SavePhaseResults(
            failed_armour_save_dist=self.failed_armour_save_roll.calc_dist()
        )

    @property
    def failed_armour_save_roll(self):
        return FailedArmourSaveRoll(
            weapon=self.weapon,
            target=self.target,
            modifiers=self.modifiers,
        )
