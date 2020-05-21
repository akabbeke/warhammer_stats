"""
A collection of classes to modify PMFs
"""

from .pmf import PMF, PMFCollection


# pylint: disable=R0201,C0302,R0913,R0904
class Modifier:
    """
    A base class used to represent a modfidier to a dice roll it includes
    the no-op stub methods for all dice operations.

    Attributes
    ----------
    priority : int
        Determines the priority order for the modifiers

    Methods
    -------
    modify_dice(col, thresh=None,  mod_thresh=None)
        Modifies the raw PMF

    modify_re_roll(col, thresh=None, mod_thresh=None)
        Modifies the dice through re-rolls

    modify_threshold(thresh)
        Modified the dice roll threshold in some way

    modify_save(save)
        Modify the save threshold in some way

    modify_ap(ap)
        Modify the armour penetration characteristic in some way

    modify_invuln(invuln)
        Modify the invulnerable save threshold in some way

    mod_extra_hit()
        Return the details for if a dice roll generates extra automatic hits
        that trigger on a modifiable threshold (eg: 5+)

    extra_hit()
        Return the details for if a dice roll generates extra automatic hits
        that trigger on an unmodifiable threshold (eg: 5 or 6)

    mod_extra_shot()
        Return the details for if a dice roll generates extra chances to hit
        that trigger on a modifiable threshold (eg: 5+)

    extra_shot()
        Return the details for if a dice roll generates extra chances to hit
        that trigger on an unmodifiable threshold (eg: 5 or 6)

    mod_extra_wound()
        Return the details for if a dice roll generates extra automatic wounds
        that trigger on a modifiable threshold (eg: 5+)

    extra_wound()
        Return the details for if a dice roll generates extra automatic wounds
        that trigger on an unmodifiable threshold (eg: 5 or 6)

    mod_mortal_wound()
        Return the details for if a dice roll generates mortal wounds that
        trigger on a modifiable threshold (eg: 5+)

    mortal_wound()
        Return the details for if a dice roll generates mortal wounds that
        trigger on an unmodifiable threshold (eg: 5 or 6)

    modify_drones()
        Return the details for if saviour protocols are active

    self_wound_thresh()
        Return the details for the to hit roll can generate wounds for the attacker
    """

    priority = 0
    # def __init__(self, keywords):
    #     self.keywords = keywords

    def modify_dice(self, col: PMFCollection, __: int, ___: int) -> PMFCollection:
        """Modifies the dice distribution. Sperate from the re-rolls becuse
        modifiers happen after re-rolls

        Parameters
        ----------
        col : PMFCollection
            The unmodified PMF collection that the modifier will be applied to
        thresh : int
            The unmodified dice success threshold, used to determine what values
            should be re-rolled. This is seperate from the modified threshold because
            "reroll failed" dice and "reroll all dice" interact with modifers
            differently
        mod_thresh : int, optional
            The modified dice success threshold, used to determine what values
            should be re-rolled (default is None)

        Returns
        -------
        PMFCollection
            The modified PMF Collection
        """
        return col

    def modify_re_roll(self, col: PMFCollection, _: int, __: int) -> PMFCollection:
        """Modifies the dice distribution via re-rolls

        Parameters
        ----------
        col : PMFCollection
            The unmodified PMF collection that the modifier will be applied to
        thresh : int
            The unmodified dice success threshold, used to determine what values
            should be re-rolled. This is seperate from the modified threshold because
            "reroll failed" dice and "reroll all dice" interact with modifers
            differently
        mod_thresh : int, optional
            The modified dice success threshold, used to determine what values
            should be re-rolled (default is None)

        Returns
        -------
        PMFCollection
            The modified PMF Collection
        """
        return col

    def modify_threshold(self, thresh: int) -> int:
        """Modifies the dice success threshold

        Parameters
        ----------
        thresh : int
            The unmodified dice success threshold

        Returns
        -------
        int
            Returns the provided dice success threshold in the base class
        """
        return thresh

    def modify_save(self, save: int) -> int:
        """Modifies the save success threshold

        Parameters
        ----------
        save : int
            The unmodified save dice success threshold

        Returns
        -------
        int
            Returns the provided save in the base class
        """
        return save

    def modify_ap(self, armour_penetration: int) -> int:
        """Modifies the armour penetration characteristic

        Parameters
        ----------
        armour_penetration : int
            The unmodified armour penetration characteristic

        Returns
        -------
        int
            Returns the provided armour penetration characteristic in the base class
        """
        return armour_penetration

    def modify_invuln(self, invuln: int) -> int:
        """Modifies the invunerable armour penetration characteristic

        Parameters
        ----------
        invuln : int
            The unmodified invunerable armour penetration characteristic

        Returns
        -------
        int
            Returns the provided invuln in the base class
        """
        return invuln

    def mod_extra_hit(self) -> PMFCollection:
        """Returns a PMF Collection of the modifiable extra hits generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def extra_hit(self) -> PMFCollection:
        """Returns a PMF Collection of the extra hits generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def mod_extra_shot(self) -> PMFCollection:
        """Returns a PMF Collection of the modifiable extra shots generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def extra_shot(self) -> PMFCollection:
        """Returns a PMF Collection of the modifiable extra shots generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def mod_extra_wound(self) -> PMFCollection:
        """Returns a PMF Collection of the modifiable extra shots generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def extra_wound(self) -> PMFCollection:
        """Returns a PMF Collection of the unmodifiable extra wounds generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def mod_mortal_wound(self) -> PMFCollection:
        """Returns a PMF Collection of the modifiable extra mortal wounds generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def mortal_wound(self) -> PMFCollection:
        """Returns a PMF Collection of the unmodifiable extra mortal wounds generated

        Returns
        -------
        PMFCollection
            Returns None in the base class
        """
        return None

    def modify_drones(self) -> tuple:
        """Returns a tuple of if saviour protocols is enabled and what the threshold for
        it is and the fnp value for the drones

        Returns
        -------
        tuple
            (False, 7, 7)
        """
        return False, 7, 7

    def self_wound_thresh(self) -> int:
        """Returns the to hit threshold for self wounds to generate below

        Returns
        -------
        int
            Base class always returns 0
        """
        return 0


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
    modify_dice(col: PMFCollection)
        Returns the PMFCollection where the PMFs have been modified to have a lower limit
    """

    def __init__(self, min_val: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_val = min_val

    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.min(self.min_val))


class ExplodingDice(Modifier):
    """
    The base class for the exploding dice modifiers.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mod_extra_hit()
        Returns the PMFCollection for the exploding dice

    _pmf_collection()
        Returns the PMFCollection for the exploding dice
    """
    def __init__(self, thresh: int, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # clamp the threshold between 0 and 7
        self.thresh = max(0, min(7, thresh))
        self.value = value

    def _pmf_collection(self) -> PMFCollection:
        return PMFCollection(
            [PMF.static(0)] * self.thresh + [PMF.static(self.value)] * (7 - self.thresh)
        )


class ModExtraHit(ExplodingDice):
    """
    Exploding dice for generating extra extra automatic hits.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mod_extra_hit()
        Returns the PMFCollection for the exploding dice
    """
    def mod_extra_hit(self) -> PMFCollection:
        return self._pmf_collection()


class ExtraHit(ExplodingDice):
    """
    Exploding dice for generating extra extra automatic hits on
    unmodified rolls.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    extra_hit()
        Returns the PMFCollection for the exploding dice
    """
    def extra_hit(self) -> PMFCollection:
        return self._pmf_collection()


class ModExtraAttack(ExplodingDice):
    """
    Exploding dice for generating extra extra attacks.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mod_extra_shot()
        Returns the PMFCollection for the exploding dice
    """
    def mod_extra_shot(self) -> PMFCollection:
        return self._pmf_collection()


class ExtraShot(ExplodingDice):
    """
    Exploding dice for generating extra extra attacks on
    unmodified rolls.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    extra_shot()
        Returns the PMFCollection for the exploding dice
    """
    def extra_shot(self) -> PMFCollection:
        return self._pmf_collection()


class ModExtraWound(ExplodingDice):
    """
    Exploding dice for generating extra automatic wounds.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mod_extra_wound()
        Returns the PMFCollection for the exploding dice
    """
    def mod_extra_wound(self) -> PMFCollection:
        return self._pmf_collection()


class ExtraWound(ExplodingDice):
    """
    Exploding dice for generating extra automatic wounds on
    unmodified rolls.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    extra_wound()
        Returns the PMFCollection for the exploding dice
    """
    def extra_wound(self) -> PMFCollection:
        return self._pmf_collection()


class GenerateMortalWound(ExplodingDice):
    """
    Exploding dice for generating mortal wounds on unmodified rolls.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mortal_wound()
        Returns the PMFCollection for the exploding dice
    """
    def mortal_wound(self) -> PMFCollection:
        return self._pmf_collection()


class ModGenerateMortalWound(ExplodingDice):
    """
    Exploding dice for generating mortal wounds.

    Attributes
    thresh : int
        The threshold value that extra dice are generated on

    value : int
        The number of extra dice generated

    Methods
    -------
    mod_mortal_wound()
        Returns the PMFCollection for the exploding dice
    """
    def mod_mortal_wound(self) -> PMFCollection:
        return self._pmf_collection()


class Haywire(ExplodingDice):
    """
    Simulating the Haywire effects.

    Methods
    -------
    mod_mortal_wound()
        Returns the PMFCollection for the exploding dice
    """
    def mod_mortal_wound(self) -> PMFCollection:
        # This is a hardcoded implementation of the haywire mechanic of generating a mortal
        # wound on 4 and 5 and D3 mortal wounds on a 6+
        col = [
            PMF.static(0), # 0 for 0
            PMF.static(0), # 0 for 1
            PMF.static(0), # 0 for 2
            PMF.static(0), # 0 for 3
            PMF.static(1), # 1 for 4
            PMF.static(1), # 1 for 5
            PMF.dn(3), # d3 for 6
        ]
        return PMFCollection(col)


class ReRollOnes(Modifier):
    """
    Simulate rerolling the one value of the distributions

    Attributes
    ----------
    priority : int
        priority = 1

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after re-rolling ones
    """
    priority = 1
    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.re_roll_value(1))


class ReRollFailed(Modifier):
    """
    Simulate rerolling the of failed rolls. Since this is only failed rolls before
    any modifiers it uses the worse value of the thresh ans mod thresh

    Attributes
    ----------
    priority : int
        priority = 99

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after re-rolling failed rolls
    """
    priority = 99
    def modify_re_roll(self, col: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        rr_thresh = min(thresh, mod_thresh)
        return col.map(lambda x: x.re_roll_less_than(rr_thresh))


class ReRollOneDice(Modifier):
    """
    Simulate rerolling the of all rolls of a single code in the PMF collection

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after re-rolling all rolls
    """
    def modify_re_roll(self, col: PMFCollection, thresh: int, _) -> PMFCollection:
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(thresh)
        return PMFCollection(pmfs)


class ReRollOneDiceVolume(Modifier):
    """
    Simulate rerolling one of the volume dice by rerolling vaues lower than the expected
    value of the dice.

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after values lower than the epected value
    """
    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(pmfs[0].mean())
        return PMFCollection(pmfs)


class ReRollAll(Modifier):
    """
    Simulate rerolling all the dice. This allows you to include negative thrshold modifiers.

    Attributes
    ----------
    priority : int
        priority = 100

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after rerolling all values
    """
    priority = 100
    def modify_re_roll(self, col: PMFCollection, _, mod_thresh: int) -> PMFCollection:
        return col.map(lambda x: x.re_roll_less_than(mod_thresh))


class ReRollLessThanExpectedValue(Modifier):
    """
    Simulate rerolling the volume dice by rerolling vaues lower than the expected
    value of the dice.

    Methods
    -------
    modify_re_roll()
        Returns the PMFCollection after values lower than the epected value
    """
    priority = 98
    def modify_re_roll(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.re_roll_less_than(x.mean()))


class HighestOfTwo(Modifier):
    """
    Simulate rolling two dice and choosing the highest

    Methods
    -------
    modify_dice()
        Returns the PMFCollection of the highest of two dice
    """
    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.max_of_two())


class AddNTo(Modifier):
    """
    Base class for modifying dice or thresholds by a set amount
    """
    def __init__(self, value: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value
        self.priority = self.value


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
        return armour_penetration - self.value


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
    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.roll(self.value))


class AddD6(AddNTo):
    """
    Adds a d6 to the volume roll

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return PMFCollection(col.pmfs+[PMF.dn(6)])


class AddD3(AddNTo):
    """
    Adds a d3 to the volume roll

    Methods
    -------
    modify_dice()
        Returns the modified PMFCollection
    """
    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return PMFCollection(col.pmfs+[PMF.dn(3)])


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
    def modify_dice(self, col: PMFCollection, *_) -> PMFCollection:
        return col.map(lambda x: x.div_min_one(2))


class ShieldDrone(Modifier):
    """
    Mark that saviour protocols are active with a threshold of 2+ and a fnp of 5+++

    Methods
    -------
    modify_drones()
        Returns drone info
    """
    def modify_drones(self) -> tuple:
        return True, 2, 5


class NormalDrone(Modifier):
    """
    Mark that saviour protocols are active with a threshold of 2+ and a fnp of 7+++

    Methods
    -------
    modify_drones()
        Returns drone info
    """
    def modify_drones(self) -> tuple:
        return True, 2, 7


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


class ModifierCollection:
    """
    Used to keep track of any modifiers to the attack
    """
    def __init__(self, shot_mods=None, hit_mods=None, wound_mods=None, pen_mods=None,
                 fnp_mods=None, damage_mods=None):

        self.shot_mods = self._sort_priority(shot_mods or [])
        self.hit_mods = self._sort_priority(hit_mods or [])
        self.wound_mods = self._sort_priority(wound_mods or [])
        self.pen_mods = self._sort_priority(pen_mods or [])
        self.fnp_mods = self._sort_priority(fnp_mods or [])
        self.damage_mods = self._sort_priority(damage_mods or [])

    def __add__(self, other):
        # Useful when you want to add two ModifierCollection together
        if not isinstance(other, ModifierCollection):
            raise TypeError(f'{other} is not ModifierCollection')

        return ModifierCollection(
            shot_mods=self.shot_mods+other.shot_mods,
            hit_mods=self.hit_mods+other.hit_mods,
            wound_mods=self.wound_mods+other.wound_mods,
            pen_mods=self.pen_mods+other.pen_mods,
            fnp_mods=self.fnp_mods+other.fnp_mods,
            damage_mods=self.damage_mods+other.damage_mods,
        )

    def _sort_priority(self, mods: list) -> list:
        return sorted(mods, key=lambda x: x.priority, reverse=True)

    def _mod_dice(self, col: PMFCollection, mods: list, thresh=None,
                  mod_thresh=None) -> PMFCollection:
        """Modifies the dice distribution

        Parameters
        ----------
        col : PMFCollection
            The unmodified PMF collection that the modifier will be applied to
        mods : list
            The list of mods to be applied
        thresh : list
            The unmodified dice success threshold, used to determine what values
            should be re-rolled. This is seperate from the modified threshold because
            "reroll failed" dice and "reroll all dice" interact with modifers
            differently
        mod_thresh : int, optional
            The modified dice success threshold, used to determine what values
            should be re-rolled (default is None)

        Returns
        -------
        PMFCollection
            The modified PMF Collection
        """
        for mod in mods:
            col = mod.modify_re_roll(col, thresh, mod_thresh)
        for mod in mods:
            col = mod.modify_dice(col, thresh, mod_thresh)
        return col

    def modify_shot_dice(self, col: PMFCollection) -> PMFCollection:
        """
        Modify the PMF of shot volume the dice. Ususally for re-rolls.
        """
        return self._mod_dice(col, self.shot_mods)

    def modify_hit_thresh(self, thresh: int) -> int:
        """
        Modify the hit threshold. Important to note the -1 to hit modifiers actually
        are a +1 to the threshold. Similarly +1 to hits are -1 to the threshold.
        """
        if thresh == 1:
            # Handle the case where the weapon is auto hit. No to hit modifiers map
            return thresh
        for mod in self.hit_mods:
            thresh = mod.modify_threshold(thresh)
        return max(thresh, 2) #1's always fail

    def modify_hit_dice(self, col: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._mod_dice(col, self.hit_mods, thresh, mod_thresh)

    def modify_wound_thresh(self, thresh: int) -> int:
        """
        Modify the wound threshold. Important to note the -1 to wound modifiers actually
        are a +1 to the threshold. Similarly +1 are -1 to the threshold.
        """
        for mod in self.wound_mods:
            thresh = mod.modify_threshold(thresh)
        return max(2, thresh) # 1's always fail

    def modify_wound_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.wound_mods, thresh, mod_thresh)

    def modify_pen_thresh(self, save, armour_penetration, invuln):
        """
        Modify the pen threshold by modifying the save, ap, and invuln
        """
        for mod in self.pen_mods:
            save = mod.modify_save(save)
        for mod in self.pen_mods:
            armour_penetration = mod.modify_ap(armour_penetration)
        for mod in self.pen_mods:
            invuln = mod.modify_invuln(invuln)
        return min(max(save + armour_penetration, 2), max(invuln, 2)) # 1's alwasys fail

    def modify_pen_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of the pen dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.pen_mods, thresh, mod_thresh)

    def modify_drone(self):
        """
        Return if the attack should be modified by saviour protocols
        """
        enabled = False
        thresh = 7
        fnp = 7
        for mod in self.pen_mods:
            mod_enabled, mod_threshold, mod_fnp = mod.modify_drones()

            enabled = enabled or mod_enabled
            thresh = thresh if thresh < mod_threshold else mod_threshold
            fnp = fnp if fnp < mod_fnp else mod_fnp

        return enabled, thresh, fnp

    def self_wound_thresh(self) -> int:
        """
        Return threshold for self wound
        """
        thresh = 0
        for mod in self.hit_mods:
            mod_thresh = mod.self_wound_thresh()
            thresh = thresh if thresh > mod_thresh else mod_thresh
        return thresh


    def modify_fnp_thresh(self, thresh):
        """
        Modify the fnp threshold. I think some death guard units can do this?
        """
        for mod in self.fnp_mods:
            thresh = mod.modify_save(thresh)
        return max(thresh, 2) # 1's alwasys fail

    def modify_fnp_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of the FNP dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.fnp_mods, thresh, mod_thresh)

    def modify_damage_dice(self, dists):
        """
        Modify the damage dice
        """
        return self._mod_dice(dists, self.damage_mods)

    def sum_generators(self, mod_list, attr_name):
        """
        Sum the generators
        """
        cols = [getattr(mod, attr_name)() for mod in mod_list]
        cols = [x for x in cols if x]
        return PMFCollection.add_many(cols)

    def get_mod_extra_hit(self):
        """
        Generate extra hits on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_extra_hit')

    def get_extra_hit(self) -> PMFCollection:
        """
        Generate extra hits on a static value
        """
        return self.sum_generators(self.hit_mods, 'extra_hit')

    def get_mod_extra_shot(self) -> PMFCollection:
        """
        Generate extra shots on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_extra_shot')

    def get_extra_shot(self) -> PMFCollection:
        """
        Generate extra shots on a static value
        """
        return self.sum_generators(self.hit_mods, 'extra_shot')

    def get_mod_extra_wound(self) -> PMFCollection:
        """
        Generate extra wounds on a modfiable value
        """
        return self.sum_generators(self.wound_mods, 'mod_extra_wound')

    def get_extra_wound(self) -> PMFCollection:
        """
        Generate extra wounds on a static value
        """
        return self.sum_generators(self.wound_mods, 'extra_wound')

    def hit_mod_mortal_wounds(self) -> PMFCollection:
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_mortal_wound')

    def wound_mod_mortal_wounds(self) -> PMFCollection:
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(self.wound_mods, 'mod_mortal_wound')

    def hit_mortal_wounds(self) -> PMFCollection:
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(self.hit_mods, 'mortal_wound')

    def wound_mortal_wounds(self) -> PMFCollection:
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(self.wound_mods, 'mortal_wound')
