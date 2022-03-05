
from . import Modifier
from .additive_modifiers import AddNToAP, AddNToVolume
from ..utils.modifier_collection import ModifierCollection


class SplitterModifier(Modifier):
    def _mod_collection(self):
        return ModifierCollection()


class OnAnUnmodifiableRollOfNAddAP(SplitterModifier):
    def __init__(self, thresh: int, extra_ap: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = thresh
        self.extra_ap = extra_ap

    def _mod_collection(self):
        return ModifierCollection(
            save_mods=[AddNToAP(self.extra_ap)]
        )

    def split_save_roll_unmodifiable(self):
        return [[self.thresh, self._mod_collection()]]

    def to_dict(self):
        return {
            **super().to_dict(),
            'thresh': self.thresh,
            'extra_ap': self.extra_ap
        }


class OnAModifiableRollOfNAddAP(SplitterModifier):
    def __init__(self, thresh: int, extra_ap: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = thresh
        self.extra_ap = extra_ap

    def _mod_collection(self):
        return ModifierCollection(
            save_mods=[AddNToAP(self.extra_ap)]
        )

    def split_save_roll_modifiable(self):
        return [[self.thresh, self._mod_collection()]]

    def to_dict(self):
        return {
            **super().to_dict(),
            'thresh': self.thresh,
            'extra_ap': self.extra_ap
        }


class OnAnUnmodifiableRollOfNAddDamage(SplitterModifier):
    def __init__(self, thresh: int, extra_damage: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = thresh
        self.extra_damage = extra_damage

    def _mod_collection(self):
        return ModifierCollection(
            damage_mods=[AddNToVolume(self.extra_damage)]
        )

    def split_damage_roll_unmodifiable(self):
        return [[self.thresh, self._mod_collection()]]

    def to_dict(self):
        return {
            **super().to_dict(),
            'thresh': self.thresh,
            'extra_damage': self.extra_damage
        }


class OnAModifiableRollOfNAddDamage(SplitterModifier):
    def __init__(self, thresh: int, extra_damage: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thresh = thresh
        self.extra_damage = extra_damage

    def _mod_collection(self):
        return ModifierCollection(
            damage_mods=[AddNToVolume(self.extra_damage)]
        )

    def split_damage_roll_modifiable(self):
        return [[self.thresh, self._mod_collection()]]

    def to_dict(self):
        return {
            **super().to_dict(),
            'thresh': self.thresh,
            'extra_damage': self.extra_damage
        }
