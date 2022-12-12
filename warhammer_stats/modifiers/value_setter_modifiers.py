from ..utils.pmf import PMFCollection
from . import Modifier


class SetToN(Modifier):
    """
    Base class of modifiers that fix the PMF or threshold to a certain value
    """
    def __init__(self, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value


class SetThresholdToN(SetToN):
    """
    Sets the threshold to N value

    Methods
    -------
    modify_threshold()
        Returns the N value
    """
    def modify_threshold(self, thresh: int) -> int:
        return self.value


class SetAPToN(SetToN):
    """
    Sets the armour pentration to N value

    Methods
    -------
    modify_ap()
        Returns the N value
    """
    def modify_ap(self, armour_penetration: int) -> int:
        return self.value


class SetSaveToN(SetToN):
    """
    Sets the save to N value

    Methods
    -------
    modify_save()
        Returns the N value
    """
    def modify_save(self, save: int) -> int:
        return self.value


class SetInvulnToN(SetToN):
    """
    Sets the invunerable save to N value

    Methods
    -------
    modify_invuln()
        Returns the N value
    """
    def modify_invuln(self, invuln: int) -> int:
        return self.value


class IgnoreAP(Modifier):
    """
    If the value is lower than N then set the ap to zero

    Methods
    -------
    modify_ap()
        Returns the N value
    """
    def __init__(self, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.armour_penetration = value

    def modify_ap(self, armour_penetration: int) -> int:
        return 0 if armour_penetration <= self.armour_penetration else armour_penetration

    def to_dict(self):
        return {
            **super().to_dict(),
            'armour_penetration': self.armour_penetration
        }


class IgnoreInvuln(Modifier):
    """
    Set the invunlerable to 7

    Methods
    -------
    modify_invuln()
        Returns 7
    """
    def modify_invuln(self, _: int) -> int:
        return 7


class HalfDamage(Modifier):
    """
    Modify the volume rolls to half the value rounding up

    Methods
    -------
    modify_invuln()
        Returns The modified PMFCollection
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.div_min_one(2))


class Overheat(Modifier):
    """
    Mark that the attack inflicts damage on the attacker

    Methods
    -------
    modify_drones()
        Return a 2+ threshold to not inflict wounds
    """
    def self_wound_thresh(self) -> int:
        return 2


class MinimumValue(Modifier):
    """
    A modifier to set a minimum value for a dice. For example some weapons that roll
    a D6 for the mount of damage state the values of one and two are considered threes.
    This adds the probability of rolling values less than the min_val to the probability
    for the min value

    Attributes
    min_val : int
        The minimum value that can be rolled on the dice

    Methods
    -------
    modify_dice(collection: PMFCollection)
        Returns the PMFCollection where the PMFs have been modified to have a lower limit
    """

    def __init__(self, min_val: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_val = min_val

    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.min(self.min_val))

    def to_dict(self):
        return {
            **super().to_dict(),
            'min_val': self.min_val,
        }


class HighestOfTwo(Modifier):
    """
    Simulate rolling two dice and choosing the highest

    Methods
    -------
    modify_dice()
        Returns the PMFCollection of the highest of two dice
    """
    def modify_dice(self, collection: PMFCollection, *_) -> PMFCollection:
        return collection.map(lambda x: x.max_of_two())
