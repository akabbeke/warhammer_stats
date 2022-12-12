from ..utils.pmf import PMF, PMFCollection
from . import Modifier

class AddNTo(Modifier):
    """
    Base class for modifying dice or thresholds by a set amount
    """
    def __init__(self, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.priority = self.value

    def to_dict(self):
        return {
            **super().to_dict(),
            'value': self.value
        }


class AddNToThreshold(AddNTo):
    """
    Add the value N to the threshold value

    Methods
    -------
    modify_threshold()
        Returns the modified threshold value
    """
    def modify_threshold(self, thresh: int) -> int:
        return thresh - self.value


class AddNToAP(AddNTo):
    """
    Add the value N to the armour penetraion value

    Methods
    -------
    modify_ap()
        Returns the modified armour penetration value
    """
    def modify_ap(self, armour_penetration: int) -> int:
        return max(armour_penetration + self.value, 0)


class AddNToSave(AddNTo):
    """
    Add the value N to the save value

    Methods
    -------
    modify_save()
        Returns the modified save value
    """
    def modify_save(self, save: int) -> int:
        return save - self.value


class AddNToInvuln(AddNTo):
    """
    Add the value N to the invunlerable save value

    Methods
    -------
    modify_invuln()
        Returns the modified save value
    """
    def modify_invuln(self, invuln: int) -> int:
        return invuln - self.value


class AddNToVolume(AddNTo):
    """
    Add the value N to the volume roll eg: d6 + 2

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.roll(self.value))


class SubtractNVolumeMinOne(AddNTo):
    """
    Subtract the value N from the volume roll eg: d6 - 1 min 1

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.roll(-1 * self.value).min(1))


class AddND6(AddNTo):
    """
    Adds a d6 to the volume roll

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return PMFCollection(collection.pmfs+[PMF.dn(6)])


class AddND3(AddNTo):
    """
    Adds a d3 to the volume roll

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return PMFCollection(collection.pmfs+[PMF.dn(3)])
