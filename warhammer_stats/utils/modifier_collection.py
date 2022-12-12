from ..utils.pmf import PMFCollection
import json
import hashlib

class ModifierCollection:
    """
    Used to keep track of any modifiers to the attack
    """
    def __init__(self, attacks_mods=None, hit_mods=None, wound_mods=None, save_mods=None,
                 fnp_mods=None, damage_mods=None):

        self.attacks_mods = self._sort_priority(attacks_mods or [])
        self.hit_mods = self._sort_priority(hit_mods or [])
        self.wound_mods = self._sort_priority(wound_mods or [])
        self.save_mods = self._sort_priority(save_mods or [])
        self.fnp_mods = self._sort_priority(fnp_mods or [])
        self.damage_mods = self._sort_priority(damage_mods or [])

    def __add__(self, other):
        # Useful when you want to add two ModifierCollection together
        if not isinstance(other, ModifierCollection):
            raise TypeError(f'{other} is not ModifierCollection')

        return ModifierCollection(
            attacks_mods=self.attacks_mods+other.attacks_mods,
            hit_mods=self.hit_mods+other.hit_mods,
            wound_mods=self.wound_mods+other.wound_mods,
            save_mods=self.save_mods+other.save_mods,
            fnp_mods=self.fnp_mods+other.fnp_mods,
            damage_mods=self.damage_mods+other.damage_mods,
        )

    def to_dict(self):
        return {
            'attacks_mods': [x.to_dict() for x in self.attacks_mods],
            'hit_mods': [x.to_dict() for x in self.hit_mods],
            'wound_mods': [x.to_dict() for x in self.wound_mods],
            'save_mods': [x.to_dict() for x in self.save_mods],
            'fnp_mods': [x.to_dict() for x in self.fnp_mods],
            'damage_mods': [x.to_dict() for x in self.damage_mods],
        }

    def __hash__(self):
        return int(hashlib.md5(json.dumps(self.to_dict(), sort_keys=True).encode("utf-8")).hexdigest(), 16)

    def _sort_priority(self, mods: list) -> list:
        return sorted(mods, key=lambda x: x.priority, reverse=True)

    def _mod_dice(self, collection: PMFCollection, mods: list, thresh=None,
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
            collection = mod.modify_re_roll(collection, thresh, mod_thresh)
        for mod in mods:
            collection = mod.modify_dice(collection, thresh, mod_thresh)
        return collection

    def _divert_dice(self, collection: PMFCollection, mods: list, thresh=None,
                     mod_thresh=None) -> PMFCollection:
        """Modifies the dice

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
            collection = mod.divert_dice(collection, thresh, mod_thresh)
        return collection

    def modify_shot_dice(self, collection: PMFCollection) -> PMFCollection:
        """
        Modify the PMF of shot volume the dice. Usually for re-rolls.
        """
        return self._mod_dice(collection, self.attacks_mods)

    def split_on_hit(self, hit_dist, hit_modifier, mod_getter, unmod_getter):
        hit_slices = [[0, ModifierCollection()]]
        for mod in self.hit_mods:
            hit_slices += self.modify_slices(
                mod_getter(mod),
                hit_modifier,
            )
            hit_slices += unmod_getter(mod)
        return self.flatten_slices(self.collect_slices(hit_slices), hit_dist)

    def split_on_wound(self, wound_dist, wound_modifier, mod_getter, unmod_getter):
        wounds_slices = [[0, ModifierCollection()]]
        for mod in self.wound_mods:
            wounds_slices += self.modify_slices(
                mod_getter(mod),
                wound_modifier
            )
            wounds_slices += unmod_getter(mod)
        return self.flatten_slices(self.collect_slices(wounds_slices), wound_dist)

    def split_hit_roll(self):
        return [[1.0, self]]

    def split_wound_roll(self, hit_dist, hit_modifier):
        flattened_hit_slices = self.split_on_hit(
            hit_dist,
            hit_modifier,
            lambda x: x.split_wound_roll_modifiable(),
            lambda x: x.split_wound_roll_unmodifiable(),
        )
        output = []
        for hit_prob, hit_mod in flattened_hit_slices:
            output.append([hit_prob, hit_mod + self])
        return output

    def split_save_roll(self, hit_dist, hit_modifier, wound_dist, wound_modifier):
        flattened_hit_slices = self.split_on_hit(
            hit_dist,
            hit_modifier,
            lambda x: x.split_save_roll_modifiable(),
            lambda x: x.split_save_roll_unmodifiable(),
        )

        flattened_wound_slices = self.split_on_wound(
            wound_dist,
            wound_modifier,
            lambda x: x.split_save_roll_modifiable(),
            lambda x: x.split_save_roll_unmodifiable(),
        )

        output = []
        for hit_prob, hit_mod in flattened_hit_slices:
            for wound_prob, wound_mod in flattened_wound_slices:
                output.append([hit_prob * wound_prob, hit_mod + wound_mod + self])
        return output

    def split_damage_roll(self, hit_dist, hit_modifier, wound_dist, wound_modifier):
        flattened_hit_slices = self.split_on_hit(
            hit_dist,
            hit_modifier,
            lambda x: x.split_damage_roll_modifiable(),
            lambda x: x.split_damage_roll_unmodifiable(),
        )

        flattened_wound_slices = self.split_on_wound(
            wound_dist,
            wound_modifier,
            lambda x: x.split_damage_roll_modifiable(),
            lambda x: x.split_damage_roll_unmodifiable(),
        )

        output = []
        for hit_prob, hit_mod in flattened_hit_slices:
            for wound_prob, wound_mod in flattened_wound_slices:
                output.append([hit_prob * wound_prob, hit_mod + wound_mod + self])
        return output

    def modify_slices(self, slices, modifier):
        return [[max(x[0]+modifier, 0), x[1]] for x in slices]

    def flatten_slices(self, slices, dist):
        output = []
        for mod, indices in slices.values():
            output.append([sum([dist.values[i] for i in indices]), mod])
        return output

    def collect_slices(self, slices, modifier=0):
        value_dict = {x: [] for x in range(7)}
        for slice_index, slice_mods in slices:
            for i in range(max(slice_index + modifier, 0), 7):
                value_dict[i].append(slice_mods)
        merged = {i: self.sum_mod_collections(value_dict[i]) for i in value_dict}
        inverted = {}
        for i in merged:
            if merged[i].__hash__() in inverted:
                inverted[merged[i].__hash__()][1].append(i)
            else:
                inverted[merged[i].__hash__()] = [merged[i], [i]]
        return inverted

    def sum_mod_collections(self, mod_collections):
        collection = ModifierCollection()
        for mod_collection in mod_collections:
            collection = collection + mod_collection
        return collection

    def modify_hit_thresh(self, thresh: int) -> int:
        """
        Modify the hit threshold. Important to note the -1 to hit modifiers actually
        are a +1 to the threshold. Similarly +1 to hits are -1 to the threshold.
        """
        for mod in self.hit_mods:
            thresh = mod.modify_threshold(thresh)
        return max(thresh, 2)  # 's always fail

    def modify_hit_dice(self, collection: PMFCollection, thresh: int, mod_thresh: int) -> PMFCollection:
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._mod_dice(collection, self.hit_mods, thresh, mod_thresh)

    def modify_wound_thresh(self, thresh: int) -> int:
        """
        Modify the wound threshold. Important to note the -1 to wound modifiers actually
        are a +1 to the threshold. Similarly +1 are -1 to the threshold.
        """
        for mod in self.wound_mods:
            thresh = mod.modify_threshold(thresh)
        return max(2, thresh)  # 1's always fail

    def modify_wound_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.wound_mods, thresh, mod_thresh)

    def modify_weapon_strength(self, strength):
        """
        Modify the strength value of the weapon
        """
        for mod in self.wound_mods:
            strength = mod.modify_strength(strength)
        return max(1, strength)

    def modify_target_toughness(self, toughness):
        """
        Modify the toughness value of the target
        """
        for mod in self.wound_mods:
            toughness = mod.modify_toughness(toughness)
        return max(1, toughness)

    def divert_wound_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of hit dice. Ususally for re-rolls.
        """
        return self._divert_dice(dists, self.wound_mods, thresh, mod_thresh)

    def modify_pen_thresh(self, save, armour_penetration, invuln):
        """
        Modify the pen threshold by modifying the save, ap, and invuln
        """
        for mod in self.save_mods:
            save = mod.modify_save(save)
        for mod in self.save_mods:
            armour_penetration = mod.modify_ap(armour_penetration)
        for mod in self.save_mods:
            invuln = mod.modify_invuln(invuln)

        return min(max(save + armour_penetration, 2), max(invuln, 2))  # 1's alwasys fail

    def modify_save_dice(self, dists, thresh, mod_thresh):
        """
        Modify the PMF of the pen dice. Ususally for re-rolls.
        """
        return self._mod_dice(dists, self.save_mods, thresh, mod_thresh)

    def modify_drone(self):
        """
        Return if the attack should be modified by saviour protocols
        """
        enabled = False
        thresh = 7
        fnp = 7
        for mod in self.save_mods:
            mod_enabled, mod_threshold, mod_fnp = mod.modify_drones()

            enabled = enabled or mod_enabled
            thresh = thresh if thresh < mod_threshold else mod_threshold
            fnp = fnp if fnp < mod_fnp else mod_fnp

        return enabled, thresh, fnp

    def hit_self_wound_thresh(self) -> int:
        """
        Return threshold for self wound
        """
        thresh = 0
        for mod in self.hit_mods:
            mod_thresh = mod.self_wound_thresh()
            thresh = thresh if thresh > mod_thresh else mod_thresh
        return thresh

    def wound_self_wound_thresh(self) -> int:
        """
        Return threshold for self wound
        """
        thresh = 0
        for mod in self.wound_mods:
            mod_thresh = mod.self_wound_thresh()
            thresh = thresh if thresh > mod_thresh else mod_thresh
        return thresh

    def modify_fnp_thresh(self, thresh):
        """
        Modify the fnp threshold. I think some death guard units can do this?
        """
        for mod in self.fnp_mods:
            thresh = mod.modify_save(thresh)
        return max(thresh, 2)  # 1's alwasys fail

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

    def extra_automatic_hit_dist_modifiable(self):
        """
        Generate extra hits on a modfiable value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_hit_modifiable'
        )

    def extra_automatic_hit_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate extra hits on a static value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_hit_unmodifiable'
        )

    def extra_hit_roll_dist_modifiable(self) -> PMFCollection:
        """
        Generate extra shots on a modfiable value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_hit_roll_modifiable'
        )

    def extra_hit_roll_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate extra shots on a static value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_hit_roll_unmodifiable'
        )

    def extra_wound_roll_dist_modifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a modfiable value
        """
        return self.sum_generators(
            self.wound_mods,
            'extra_wounds_rolls_modifiable'
        )

    def extra_wound_roll_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a static value
        """
        return self.sum_generators(
            self.wound_mods,
            'extra_wounds_rolls_unmodifiable'
        )

    def hit_generated_mortal_wounds_dist_modifiable(self) -> PMFCollection:
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_mortal_wound_modifiable'
        )

    def wound_generated_mortal_wounds_dist_modifiable(self) -> PMFCollection:
        """
        Generate mortal wounds on a modfiable value
        """
        return self.sum_generators(
            self.wound_mods,
            'extra_mortal_wound_modifiable'
        )

    def hit_generated_mortal_wounds_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_mortal_wound_unmodifiable'
        )

    def wound_generated_mortal_wounds_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate mortal wounds on a static value
        """
        return self.sum_generators(
            self.wound_mods,
            'extra_mortal_wound_unmodifiable'
        )

    def hit_generated_extra_automatic_wound_dist_modifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a modfiable value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_wounds_modifiable'
        )

    def hit_generated_extra_automatic_wound_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a static value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_wounds_unmodifiable'
        )

    def wound_generated_extra_automatic_wound_dist_modifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a modfiable value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_wounds_modifiable'
        )

    def wound_generated_extra_automatic_wound_dist_unmodifiable(self) -> PMFCollection:
        """
        Generate extra wounds on a static value
        """
        return self.sum_generators(
            self.hit_mods,
            'extra_automatic_wounds_unmodifiable'
        )
