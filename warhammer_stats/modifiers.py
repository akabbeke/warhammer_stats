from .pmf import PMF, PMFCollection


class Modifier(object):
    """
    Base class for Modifiers. 'priority' is used for order of opperations and
    for re-rolls it determines the which re-roll is applied.
    e.g. full re-roll > re-roll failed > re-roll 1s
    """
    priority = 0
    def __init__(self, *args, **kwargs):
        pass

    def modify_dice(self, col, thresh=None,  mod_thresh=None):
        return col

    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        return col

    def modify_threshold(self, thresh):
        return thresh

    def modify_save(self, save):
        return save

    def modify_ap(self, ap):
        return ap

    def modify_invuln(self, invuln):
        return invuln

    def mod_extra_hit(self):
        return None

    def extra_hit(self):
        return None

    def mod_extra_shot(self):
        return None

    def extra_shot(self):
        return None

    def mod_extra_wound(self):
        return None

    def extra_wound(self):
        return None

    def mod_mortal_wound(self):
        return None

    def mortal_wound(self):
        return None

    def modify_drones(self):
        return False, 7, 7

    def modify_self_wounds(self):
        return 0


class MinimumValue(Modifier):
    def __init__(self, min_val):
        self.min_val = min_val

    def modify_dice(self, col, thresh=None,  mod_thresh=None):
        return col.map(lambda x: x.min(self.min_val))


class ExplodingDice(Modifier):
    def __init__(self, thresh, value):
        self.thresh = max(0, min(7, thresh))
        self.value = value

    def _pmf_collection(self):
        return PMFCollection([PMF.static(0)] * self.thresh + [PMF.static(self.value)] * (7 - self.thresh))


class ModExtraHit(ExplodingDice):
    def mod_extra_hit(self):
        return self._pmf_collection()


class ExtraHit(ExplodingDice):
    def extra_hit(self):
        return self._pmf_collection()


class ModExtraAttack(ExplodingDice):
    def mod_extra_shot(self):
        return self._pmf_collection()


class ExtraShot(ExplodingDice):
    def extra_shot(self):
        return self._pmf_collection()


class ModExtraWound(ExplodingDice):
    def mod_extra_wound(self):
        return self._pmf_collection()


class ExtraWound(ExplodingDice):
    def extra_wound(self):
        return self._pmf_collection()


class GenerateMortalWound(ExplodingDice):
    def mortal_wound(self):
        return self._pmf_collection()


class ModGenerateMortalWound(ExplodingDice):
    def mod_mortal_wound(self):
        return self._pmf_collection()


class Haywire(ExplodingDice):
    def mod_mortal_wound(self):
        col = [PMF.static(0), PMF.static(0), PMF.static(0), PMF.static(0), PMF.static(1), PMF.static(1), PMF.dn(3)]
        return PMFCollection(col)


class ReRollOnes(Modifier):
    priority = 1
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.re_roll_value(1))


class ReRollFailed(Modifier):
    priority = 99
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        rr_thresh = min(thresh, mod_thresh)
        return col.map(lambda x: x.re_roll_less_than(rr_thresh))


class ReRollOneDice(Modifier):
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(thresh)
        return PMFCollection(pmfs)

class ModReRollOneDice(Modifier):
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(mod_thresh)
        return PMFCollection(pmfs)


class ReRollOneDiceVolume(Modifier):
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        pmfs = col.pmfs
        if not pmfs:
            return col
        pmfs[0] = pmfs[0].re_roll_less_than(pmfs[0].mean())
        return PMFCollection(pmfs)


class ReRollAll(Modifier):
    priority = 100
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.re_roll_less_than(mod_thresh))


class ReRollLessThanExpectedValue(Modifier):
    priority = 98
    def modify_re_roll(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.re_roll_less_than(x.mean()))


class Melta(Modifier):
    def modify_dice(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.melta())


class AddNTo(Modifier):
    def __init__(self, value=0, *args, **kwargs):
        self.n = value
        self.priority = self.n


class AddNToThreshold(AddNTo):
    def modify_threshold(self, thresh):
        return thresh - self.n


class AddNToAP(AddNTo):
    def modify_ap(self, ap):
        return ap - self.n


class AddNToSave(AddNTo):
    def modify_save(self, save):
        return save - self.n


class AddNToInvuln(AddNTo):
    def modify_invuln(self, invuln):
        return invuln - self.n


class AddNToVolume(AddNTo):
    def modify_dice(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.roll(self.n))


class AddD6(AddNTo):
    def modify_dice(self, col, thresh=None, mod_thresh=None):
        return PMFCollection(col.pmfs+[PMF.dn(6)])


class AddD3(AddNTo):
    def modify_dice(self, col, thresh=None, mod_thresh=None):
        return PMFCollection(col.pmfs+[PMF.dn(3)])


class SetToN(Modifier):
    def __init__(self, value=0, *args, **kwargs):
        self.n = value


class SetThresholdToN(SetToN):
    def modify_threshold(self, thresh):
        return self.n


class SetAPToN(SetToN):
    def modify_ap(self, ap):
        return self.n


class SetSaveToN(SetToN):
    def modify_save(self, save):
        return self.n


class SetInvulnToN(SetToN):
    def modify_invuln(self, invuln):
        return self.n


class IgnoreAP(Modifier):
    def __init__(self, value=0, *args, **kwargs):
        self.ap = value

    def modify_ap(self, ap):
        return 0 if ap <= self.ap else ap


class IgnoreInvuln(Modifier):
    def modify_invuln(self, ap):
        return 7


class HalfDamage(Modifier):
    def modify_dice(self, col, thresh=None, mod_thresh=None):
        return col.map(lambda x: x.div_min_one(2))


class ShieldDrone(Modifier):
    def modify_drones(self):
        return True, 2, 5


class NormalDrone(Modifier):
    def modify_drones(self):
        return True, 2, 7


class Overheat(Modifier):
    def modify_self_wounds(self):
        return 2


class ModifierCollection(object):
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
        return ModifierCollection(
            shot_mods=self.shot_mods+other.shot_mods,
            hit_mods=self.hit_mods+other.hit_mods,
            wound_mods=self.wound_mods+other.wound_mods,
            pen_mods=self.pen_mods+other.pen_mods,
            fnp_mods=self.fnp_mods+other.fnp_mods,
            damage_mods=self.damage_mods+other.damage_mods,
        )

    def _sort_priority(self, mods ):
        return sorted(mods, key=lambda x: x.priority, reverse=True)

    def _mod_dice(self, col, mods, thresh=None, mod_thresh=None):
        """
        Apply dice modifications. Rerolls happen before modifiers.
        """
        for mod in mods:
            col = mod.modify_re_roll(col, thresh, mod_thresh)
        for mod in mods:
            col = mod.modify_dice(col, thresh, mod_thresh)
        return col

    def modify_shot_dice(self, dists):
        """
        Modify the PMF of shot volume the dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.shot_mods)

    def modify_hit_thresh(self, thresh):
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

    def modify_hit_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.hit_mods, thresh, mod_thresh)

    def modify_wound_thresh(self, thresh):
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

    def modify_pen_thresh(self, save, ap, invuln):
        """
        Modify the pen threshold by modifying the save, ap, and invuln
        """
        for mod in self.pen_mods:
            save = mod.modify_save(save)
        for mod in self.pen_mods:
            ap = mod.modify_ap(ap)
        for mod in self.pen_mods:
            invuln = mod.modify_invuln(invuln)
        return min(max(save + ap, 2), max(invuln, 2)) # 1's alwasys fail

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
            e, t, f = mod.modify_drones()

            enabled = enabled or e
            thresh = thresh if thresh < t else t
            fnp = fnp if fnp < f else f

        return enabled, thresh, fnp

    def modify_self_wounds(self):
        """
        Return threshold for self wound
        """
        thresh = 0
        for mod in self.hit_mods:
            mod_thresh = mod.modify_self_wounds()
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
        cols = [getattr(mod, attr_name)() for mod in mod_list]
        cols = [x for x in cols if x]
        return PMFCollection.add_many(cols)

    def get_mod_extra_hit(self):
        """
        Generate extra hits on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_extra_hit')

    def get_extra_hit(self):
        """
        Generate extra hits on a static value
        """
        return self.sum_generators(self.hit_mods, 'extra_hit')

    def get_mod_extra_shot(self):
        """
        Generate extra shots on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_extra_shot')

    def get_extra_shot(self):
        """
        Generate extra shots on a static value
        """
        return self.sum_generators(self.hit_mods, 'extra_shot')

    def get_mod_extra_wound(self):
        """
        Generate extra wounds on a modfiable value
        """
        return self.sum_generators(self.wound_mods, 'mod_extra_wound')

    def get_extra_wound(self):
        """
        Generate extra wounds on a static value
        """
        return self.sum_generators(self.wound_mods, 'extra_wound')

    def hit_mod_mortal_wounds(self):
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(self.hit_mods, 'mod_mortal_wound')

    def wound_mod_mortal_wounds(self):
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(self.wound_mods, 'mod_mortal_wound')

    def hit_mortal_wounds(self):
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(self.hit_mods, 'mortal_wound')

    def wound_mortal_wounds(self):
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(self.wound_mods, 'mortal_wound')
