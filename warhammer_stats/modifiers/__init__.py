from ..utils.pmf import PMFCollection


# pylint: disable=R0201,C0302,R0913,R0904
class Modifier:
    priority = 0

    def to_dict(self):
        return {'name': self.__class__.__name__}

    def modify_dice(self, col: PMFCollection, __: int, ___: int) -> PMFCollection:
        return col

    def modify_re_roll(self, col: PMFCollection, _: int, __: int) -> PMFCollection:
        return col

    def modify_threshold(self, thresh: int) -> int:
        return thresh

    def modify_save(self, save: int) -> int:
        return save

    def modify_ap(self, armour_penetration: int) -> int:
        return armour_penetration

    def modify_invuln(self, invuln: int) -> int:
        return invuln

    def modify_strength(self, strength: int) -> int:
        return strength

    def modify_toughness(self, toughness) -> int:
        return toughness

    def extra_automatic_hit_modifiable(self) -> PMFCollection:
        return None

    def extra_automatic_hit_unmodifiable(self) -> PMFCollection:
        return None

    def extra_hit_roll_modifiable(self) -> PMFCollection:
        return None

    def extra_hit_roll_unmodifiable(self) -> PMFCollection:
        return None

    def extra_automatic_wounds_modifiable(self) -> PMFCollection:
        return None

    def extra_automatic_wounds_unmodifiable(self) -> PMFCollection:
        return None

    def extra_wounds_rolls_modifiable(self) -> PMFCollection:
        return None

    def extra_wounds_rolls_unmodifiable(self) -> PMFCollection:
        return None

    def extra_mortal_wound_modifiable(self) -> PMFCollection:
        return None

    def extra_mortal_wound_unmodifiable(self) -> PMFCollection:
        return None

    def self_wound_thresh(self) -> int:
        return 0

    def split_wound_roll_unmodifiable(self):
        return []

    def split_save_roll_unmodifiable(self):
        return []

    def split_damage_roll_unmodifiable(self):
        return []

    def split_wound_roll_modifiable(self):
        return []

    def split_save_roll_modifiable(self):
        return []

    def split_damage_roll_modifiable(self):
        return []
